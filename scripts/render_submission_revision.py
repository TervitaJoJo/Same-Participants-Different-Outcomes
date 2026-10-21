"""Redraw revised One Health displays from saved, auditable analysis outputs."""
from pathlib import Path
import argparse
import importlib.util
import json
import shutil
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AMR = ROOT / 'one_health_amr'
BLUE, RED, TEAL, GREY = '#1f5a94', '#c44e52', '#168579', '#b5bec7'
plt.rcParams.update({'font.family':'Arial','font.size':8,'axes.labelsize':8,
 'xtick.labelsize':7.5,'ytick.labelsize':7.5,'axes.spines.top':False,
 'axes.spines.right':False,'figure.facecolor':'white','axes.facecolor':'white',
 'pdf.fonttype':42,'ps.fonttype':42})

def save(fig, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    for ext in ['pdf','png','tif']:
        options = {'pil_kwargs':{'compression':'tiff_lzw'}} if ext=='tif' else {}
        fig.savefig(path.with_suffix('.'+ext), dpi=600, facecolor='white', **options)
    plt.close(fig)

def letter(ax, s):
    ax.text(0, 1.05, s, transform=ax.transAxes, fontweight='bold', fontsize=11)

def inherited_panel_labels(fig, axes):
    # Reserve physical headroom; fixed-size export must not clip panel letters.
    fig.subplots_adjust(top=.89)
    for s,ax in zip('AB',axes):
        fig.text(ax.get_position().x0, .94, s, fontsize=11, fontweight='bold',va='center')

def simulation(out):
    d=pd.read_csv(AMR/'checks/sim/summary.csv')
    d=d[d.metric.eq('delta')].set_index('method')
    keys=['historical_screen','joint_without_screen','saturated_paired_binary','empirical_joint']
    d=d.loc[keys]
    assert d.valid_intervals.tolist()==[12,12,359,359]
    fig=plt.figure(figsize=(174/25.4,95/25.4))
    gs=fig.add_gridspec(1,2,width_ratios=[.7,1.8],wspace=.78,
                        left=.08,right=.97,bottom=.27,top=.88)
    a=fig.add_subplot(gs[0]); b=fig.add_subplot(gs[1])
    a.bar([0],[12],color=TEAL,width=.55,label='Valid / covering')
    a.bar([0],[388],bottom=[12],color=GREY,width=.55,label='Failed')
    a.set_ylim(0,420); a.set_yticks([0,100,200,300,400]);a.set_ylabel('Attempts')
    a.set_xticks([0],['Original\nprocedure'])
    a.legend(frameon=False,fontsize=7,loc='upper left',bbox_to_anchor=(-.15,-.19))
    yy=np.arange(4)[::-1]
    for off,col,color,marker,label in [(.17,'finite_points',BLUE,'o','Finite point'),
         (0,'valid_intervals',TEAL,'s','Nondegenerate interval'),
         (-.17,'covered',RED,'D','Covering interval')]:
        b.scatter(d[col],yy+off,c=color,marker=marker,s=24,label=label,zorder=3)
    b.set_yticks(yy,['Original joint\nwith screen','Joint without\npre-screen',
                     'Saturated paired\nbinary regression','Empirical\nstandardization'])
    b.set_xlim(-10,420); b.set_xticks([0,100,200,300,400]);b.set_xlabel('Number of 400 attempts')
    b.grid(axis='x',color='#e2e5e8',lw=.6);b.set_axisbelow(True)
    b.legend(frameon=False,fontsize=7,loc='upper left',bbox_to_anchor=(-.38,-.22),ncol=2)
    letter(a,'A');letter(b,'B')
    save(fig,out/'figures/Figure2_simulation_denominator_trap')

def amr(out):
    p=pd.read_csv(AMR/'results/paired_estimates.csv')
    q=pd.read_csv(AMR/'results/descriptive_point_estimates.csv')
    c=pd.read_csv(AMR/'checks/composition/estimates.csv')
    c=c[c.uncertainty.eq('serovar_cluster')]
    selections=[('crude','all_candidate','All records\n(n=2,537)'),
      ('crude_restricted','shared_serovar','Shared serovars, crude\n(n=1,462)'),
      ('empirical_standardization','shared_serovar','Shared serovars, standardized\n(n=1,462)'),
      ('empirical_standardization','shared_serovar_year','Shared serovar-year, standardized\n(n=460)'),
      ('empirical_standardization','known_shared_serovar','Known shared serovars, standardized\n(n=1,305)'),
      ('empirical_standardization','known_shared_serovar_year','Known shared serovar-year, standardized\n(n=328)')]
    fig=plt.figure(figsize=(174/25.4,174/25.4))
    gs=fig.add_gridspec(2,2,height_ratios=[.68,1.55],wspace=.20,hspace=.52,
                       left=.39,right=.97,bottom=.10,top=.94)
    a=fig.add_subplot(gs[0,:]);b=fig.add_subplot(gs[1,0]);z=fig.add_subplot(gs[1,1])
    for j,(key,label) in enumerate([('primary_turkey','Ground turkey'),
                                   ('secondary_pork','Pork chop'),('secondary_beef','Ground beef')]):
        for off,metric,color,marker in [(.10,'logOR_M',BLUE,'o'),(-.10,'logOR_S',RED,'s')]:
            r=p[p.analysis.eq(key)&p.metric.eq(metric)&p.uncertainty.eq('source_stratified_isolate')]
            if len(r):
                r=r.iloc[0]; x,lo,hi=np.exp([r.estimate,r.low,r.high])
                a.errorbar(x,2-j+off,xerr=[[x-lo],[hi-x]],fmt=marker,color=color,ms=4,capsize=2,lw=1)
            else:
                r=q[q.analysis.eq(key)&q.metric.eq(metric)].iloc[0]
                a.plot(np.exp(r.estimate),2-j+off,marker=marker,mfc='white',mec=color,ms=5)
    a.set_yticks([2,1,0],['Ground turkey','Pork chop','Ground beef'])
    a.set_xscale('log');a.axvline(1,color='#555555',lw=.9)
    a.set_xticks([.25,.5,1],['0.25','0.5','1']);a.minorticks_off()
    a.set_xlabel('Tetracycline source OR (95% CI), vs chicken breast')
    from matplotlib.lines import Line2D
    a.legend(handles=[Line2D([],[],color=BLUE,marker='o',ls='',label='Phenotype'),
                      Line2D([],[],color=RED,marker='s',ls='',label='Genomic')],
             frameon=False,ncol=2,fontsize=7,loc='upper left',bbox_to_anchor=(0,1.25))
    yy=np.arange(len(selections))[::-1]
    for y,(model,target,label) in zip(yy,selections):
        r=c[c.model.eq(model)&c.target.eq(target)].set_index('metric')
        for off,metric,color,marker in [(.10,'logOR_M',BLUE,'o'),(-.10,'logOR_S',RED,'s')]:
            b.plot(np.exp(r.loc[metric,'estimate']),y+off,marker=marker,color=color,ms=4)
        row=r.loc['delta'];z.errorbar(row.estimate,y,xerr=[[row.estimate-row.low],[row.high-row.estimate]],
                          fmt='o',color=TEAL,ms=4,capsize=2,lw=1)
    b.set_yticks(yy,[s[2] for s in selections]);z.set_yticks(yy,[])
    b.set_xscale('log');b.set_xlim(.07,3.1);b.set_xticks([.1,.5,1,2],['0.1','0.5','1','2'])
    b.axvline(1,color='#555555',lw=.9);b.set_xlabel('Threshold-specific OR')
    b.legend(handles=[Line2D([],[],color=BLUE,marker='o',ls='',label='R'),
                      Line2D([],[],color=RED,marker='s',ls='',label='R-or-I')],frameon=False,ncol=2,
             fontsize=7,loc='upper center',bbox_to_anchor=(.5,-.12))
    z.axvline(0,color='#555555',lw=.9);z.set_xlim(-2.6,.5);z.set_xticks([-2,-1,0]);z.set_xlabel('Paired log-OR difference\n(95% CI)')
    for ax in [a,b,z]:
        ax.grid(axis='x',color='#e2e5e8',lw=.6);ax.set_axisbelow(True)
    for ax,s in zip([a,b,z],'ABC'):letter(ax,s)
    save(fig,out/'figures/Figure4_food_chain_AMR')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'outputs')
    parser.add_argument('--main-only',action='store_true')
    args=parser.parse_args();out=args.output.resolve()
    # Existing aggregate plots preserve the original source mappings and filters.
    sys.path.insert(0,str(ROOT/'scripts'))
    import render_figures as old
    def export(fig,name,supplementary=False):
        save(fig,out/('supplementary_figures' if supplementary else 'figures')/name)
    old.save=export
    old.label_panels=inherited_panel_labels
    old.configure_output(out)
    rev,sim,states,bridge,cvai,contrasts,flow,fail,charls,hrs=old.load_inputs()
    old.fig1(rev);old.fig3(states,charls)
    # Reassign the supporting graphic to S7 rather than retaining a fifth main figure.
    old.save=lambda fig,name,supplementary=False: save(fig,out/'supplementary_figures/SupplementaryFigureS7_external_evidence')
    if not args.main_only:old.fig4(cvai,hrs)
    old.save=export
    if not args.main_only:
        old.supp_s1(rev);old.supp_s2(flow);old.supp_s3(sim);old.supp_s4(fail);old.supp_s5(states);old.supp_s6(contrasts)
    simulation(out);amr(out)
    (out/'submission_figure_manifest.json').write_text(json.dumps({'raster_dpi':600,
       'main_figures':4,'supplementary_figures':7,'white_background':True,
       'inputs':'Saved aggregate, public AMR, and synthetic diagnostic outputs'},indent=2)+'\n')
    print('Rendered revised main figures 1-4 and supplementary figures S1-S7 at 600 dpi.')

if __name__=='__main__':main()
