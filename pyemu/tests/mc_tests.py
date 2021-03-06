
def mc_test():
    import os
    import numpy as np
    from pyemu import MonteCarlo
    jco = os.path.join("pst","pest.jcb")
    pst = jco.replace(".jcb",".pst")

    out_dir = os.path.join("mc")
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    #write testing
    mc = MonteCarlo(jco=jco,verbose=True)
    mc.draw(10,obs=True)
    mc.write_psts(os.path.join("mc","real_"))
    mc.parensemble.to_parfiles(os.path.join("mc","real_"))
    mc = MonteCarlo(jco=jco,verbose=True)
    mc.draw(10,obs=True)
    print("prior ensemble variance:",
          np.var(mc.parensemble.loc[:,"mult1"]))
    projected_en = mc.project_parensemble(inplace=False)
    print("projected ensemble variance:",
          np.var(projected_en.loc[:,"mult1"]))

    import pyemu
    sc = pyemu.Schur(jco=jco)

    mc = MonteCarlo(pst=pst,parcov=sc.posterior_parameter,verbose=True)
    mc.draw(10)
    print("posterior ensemble variance:",
          np.var(mc.parensemble.loc[:,"mult1"]))

def fixed_par_test():
    import os
    import numpy as np
    from pyemu import MonteCarlo
    jco = os.path.join("pst","pest.jcb")
    pst = jco.replace(".jcb",".pst")
    mc = MonteCarlo(jco=jco,pst=pst)
    mc.pst.parameter_data.loc["mult1","partrans"] = "fixed"
    mc.draw(10)
    assert np.all(mc.parensemble.loc[:,"mult1"] ==
                  mc.pst.parameter_data.loc["mult1","parval1"])


def uniform_draw_test():
    import os
    import numpy as np
    from pyemu import MonteCarlo
    jco = os.path.join("pst","pest.jcb")
    pst = jco.replace(".jcb",".pst")
    mc = MonteCarlo(jco=jco,pst=pst)
    from datetime import datetime
    start = datetime.now()
    mc.draw(num_reals=1000,how="uniform")
    print(datetime.now() - start)
    import matplotlib.pyplot as plt
    ax = mc.parensemble.loc[:,"mult1"].plot(kind="hist",bins=50,alpha=0.5)
    mc.draw(num_reals=1000)
    mc.parensemble.loc[:,"mult1"].plot(kind="hist",bins=50,ax=ax,alpha=0.5)
    #plt.show()


def write_regul_test():
    import os
    import numpy as np
    from pyemu import MonteCarlo

    mc = MonteCarlo(jco=os.path.join("verf_results","freyberg_ord.jco"))
    mc.pst.control_data.pestmode = "regularization"
    mc.draw(10)
    mc.write_psts(os.path.join("temp","freyberg_real"),existing_jco="freyberg_ord.jco")


def from_dataframe_test():
    import os
    import numpy as np
    import pandas as pd
    from pyemu import MonteCarlo,Ensemble,ParameterEnsemble,Pst

    jco = os.path.join("pst","pest.jcb")
    pst = jco.replace(".jcb",".pst")
    mc = MonteCarlo(jco=jco,pst=pst)
    names = ["par_{0}".format(_) for _ in range(10)]
    df = pd.DataFrame(np.random.random((10,mc.pst.npar)),columns=mc.pst.par_names)
    mc.parensemble = ParameterEnsemble.from_dataframe(df=df,pst=mc.pst)
    print(mc.parensemble.shape)
    mc.project_parensemble()
    mc.parensemble.to_csv(os.path.join("temp","test.csv"))

def scale_offset_test():
    import os
    import pyemu
    pst = pyemu.Pst(os.path.join("pst","scale_offest_test.pst"))
    par = pst.parameter_data
    print(par)
    en1 = pyemu.ParameterEnsemble(pst)
    en1.draw(pyemu.Cov.from_parameter_data(pst),num_reals=1000)
    en2 = pyemu.ParameterEnsemble(pst)
    en2.draw(cov=None,num_reals=1000,how="uniform")
    print(en1)
    print(en2)
    # import matplotlib.pyplot as plt
    #
    # for par in en1.columns:
    #     ax = en1.loc[:,par].plot(kind="hist",bins=50)
    #     en2.loc[:,par].plot(kind="hist",bins=50,ax=ax)
    #     ax.set_title(par)
    #     plt.show()


if __name__ == "__main__":
    #scale_offset_test()
    mc_test()
    #fixed_par_test()
    #uniform_draw_test()
    #write_regul_test()
    #from_dataframe_test()
