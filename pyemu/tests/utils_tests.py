
def fac2real_test():
    import os
    import pyemu
    pp_file = os.path.join("utils","points1.dat")
    factors_file = os.path.join("utils","factors1.dat")
    pyemu.utils.gw_utils.fac2real(pp_file,factors_file,
                                  out_file=os.path.join("utils","test.ref"))


def vario_test():
    import numpy as np
    import pyemu
    contribution = 0.1
    a = 2.0
    for const in [pyemu.utils.geostats.ExpVario,pyemu.utils.geostats.GauVario,
                  pyemu.utils.geostats.SphVario]:

        v = const(contribution,a)
        h = v.h_function(np.array([0.0]))
        assert h == contribution
        h = v.h_function(np.array([a*1000]))
        assert h == 0.0

        v2 = const(contribution,a,anisotropy=2.0,bearing=90.0)
        print(v2.h_function(np.array([a])))


def aniso_test():

    import pyemu
    contribution = 0.1
    a = 2.0
    for const in [pyemu.utils.geostats.ExpVario,pyemu.utils.geostats.GauVario,
                  pyemu.utils.geostats.SphVario]:

        v = const(contribution,a)
        v2 = const(contribution,a,anisotropy=2.0,bearing=90.0)
        v3 = const(contribution,a,anisotropy=2.0,bearing=0.0)
        pt0 = (0,0)
        pt1 = (1,0)
        assert v.covariance(pt0,pt1) == v2.covariance(pt0,pt1)

        pt0 = (0,0)
        pt1 = (0,1)
        assert v.covariance(pt0,pt1) == v3.covariance(pt0,pt1)

def geostruct_test():
    import pyemu
    v1 = pyemu.utils.geostats.ExpVario(0.1,2.0)
    v2 = pyemu.utils.geostats.GauVario(0.1,2.0)
    v3 = pyemu.utils.geostats.SphVario(0.1,2.0)

    g = pyemu.utils.geostats.GeoStruct(0.2,[v1,v2,v3])
    pt0 = (0,0)
    pt1 = (0,0)
    print(g.covariance(pt0,pt1))
    assert g.covariance(pt0,pt1) == 0.5

    pt0 = (0,0)
    pt1 = (1.0e+10,0)
    assert g.covariance(pt0,pt1) == 0.2

def struct_file_test():
    import os
    import pyemu
    struct = pyemu.utils.geostats.read_struct_file(
            os.path.join("utils","struct.dat"))[0]
    print(struct)
    pt0 = (0,0)
    pt1 = (0,0)
    assert struct.covariance(pt0,pt1) == struct.nugget + \
                                         struct.variograms[0].contribution


def covariance_matrix_test():
    import os
    import pandas as pd
    import pyemu

    pts = pd.read_csv(os.path.join("utils","points1.dat"),delim_whitespace=True,
                      header=None,names=["name","x","y"],usecols=[0,1,2])
    struct = pyemu.utils.geostats.read_struct_file(
            os.path.join("utils","struct.dat"))[0]
    struct.variograms[0].covariance_matrix(pts.x,pts.y,names=pts.name)

    print(struct.covariance_matrix(pts.x,pts.y,names=pts.name).x)


def setup_ppcov_simple():
    import os
    import platform

    exe_file = os.path.join("utils","ppcov.exe")
    print(platform.platform())
    if not os.path.exists(exe_file) or not platform.platform().lower().startswith("win"):
        print("can't run ppcov setup")
        return
    pts_file = os.path.join("utils","points1_test.dat")
    str_file = os.path.join("utils","struct_test.dat")

    args1 = [pts_file,'0.0',str_file,"struct1",os.path.join("utils","ppcov.struct1.out"),'','']
    args2 = [pts_file,'0.0',str_file,"struct2",os.path.join("utils","ppcov.struct2.out"),'','']
    args3 = [pts_file,'0.0',str_file,"struct3",os.path.join("utils","ppcov.struct3.out"),'','']


    for args in [args1,args2,args3]:
        in_file = os.path.join("utils","ppcov.in")
        with open(in_file,'w') as f:
            f.write('\n'.join(args))
        os.system(exe_file + '<' + in_file)



def ppcov_simple_test():
    import os
    import numpy as np
    import pandas as pd
    import pyemu

    pts_file = os.path.join("utils","points1_test.dat")
    str_file = os.path.join("utils","struct_test.dat")

    mat1_file = os.path.join("utils","ppcov.struct1.out")
    mat2_file = os.path.join("utils","ppcov.struct2.out")
    mat3_file = os.path.join("utils","ppcov.struct3.out")

    ppc_mat1 = pyemu.Cov.from_ascii(mat1_file)
    ppc_mat2 = pyemu.Cov.from_ascii(mat2_file)
    ppc_mat3 = pyemu.Cov.from_ascii(mat3_file)

    pts = pd.read_csv(pts_file,header=None,names=["name","x","y"],usecols=[0,1,2],
                      delim_whitespace=True)

    struct1,struct2,struct3 = pyemu.utils.geostats.read_struct_file(str_file)
    print(struct1)
    print(struct2)
    print(struct3)

    for mat,struct in zip([ppc_mat1,ppc_mat2,ppc_mat3],[struct1,struct2,struct3]):

        str_mat = struct.covariance_matrix(x=pts.x,y=pts.y,names=pts.name)
        delt = mat.x - str_mat.x
        assert np.abs(delt).max() < 1.0e-7

def setup_ppcov_complex():
    import os
    import platform

    exe_file = os.path.join("utils","ppcov.exe")
    print(platform.platform())
    if not os.path.exists(exe_file) or not platform.platform().lower().startswith("win"):
        print("can't run ppcov setup")
        return
    pts_file = os.path.join("utils","points1_test.dat")
    str_file = os.path.join("utils","struct_complex.dat")

    args1 = [pts_file,'0.0',str_file,"struct1",os.path.join("utils","ppcov.complex.struct1.out"),'','']
    args2 = [pts_file,'0.0',str_file,"struct2",os.path.join("utils","ppcov.complex.struct2.out"),'','']

    for args in [args1,args2]:
        in_file = os.path.join("utils","ppcov.in")
        with open(in_file,'w') as f:
            f.write('\n'.join(args))
        os.system(exe_file + '<' + in_file)



def ppcov_complex_test():
    import os
    import numpy as np
    import pandas as pd
    import pyemu

    pts_file = os.path.join("utils","points1_test.dat")
    str_file = os.path.join("utils","struct_complex.dat")

    mat1_file = os.path.join("utils","ppcov.complex.struct1.out")
    mat2_file = os.path.join("utils","ppcov.complex.struct2.out")

    ppc_mat1 = pyemu.Cov.from_ascii(mat1_file)
    ppc_mat2 = pyemu.Cov.from_ascii(mat2_file)

    pts = pd.read_csv(pts_file,header=None,names=["name","x","y"],usecols=[0,1,2],
                      delim_whitespace=True)

    struct1,struct2 = pyemu.utils.geostats.read_struct_file(str_file)
    print(struct1)
    print(struct2)

    for mat,struct in zip([ppc_mat1,ppc_mat2],[struct1,struct2]):

        str_mat = struct.covariance_matrix(x=pts.x,y=pts.y,names=pts.name)
        delt = mat.x - str_mat.x
        print(mat.x[:,0])
        print(str_mat.x[:,0])


        print(np.abs(delt).max())

        assert np.abs(delt).max() < 1.0e-7
        #break

def pp_to_tpl_test():
    import os
    import pyemu
    pp_file = os.path.join("utils","points1.dat")
    pp_df = pyemu.gw_utils.pilot_points_to_tpl(pp_file,name_prefix="test_")
    print(pp_df.columns)


def to_mps_test():
    import os
    import pyemu
    jco_file = os.path.join("utils","dewater_pest.jcb")
    jco = pyemu.Jco.from_binary(jco_file)
    print(jco.x)
    pst = pyemu.Pst(jco_file.replace(".jcb",".pst"))
    print(pst.nnz_obs_names)
    oc_dict = {oc:"l" for oc in pst.nnz_obs_names}
    obj_func = {name:1.0 for name in pst.par_names}

    #pyemu.optimization.to_mps(jco=jco_file)
    #pyemu.optimization.to_mps(jco=jco_file,obs_constraint_sense=oc_dict)
    #pyemu.optimization.to_mps(jco=jco_file,obj_func="h00_00")
    pyemu.optimization.to_mps(jco=jco_file,obj_func=obj_func)












if __name__ == "__main__":
    to_mps_test()
    #pp_to_tpl_test()
    # setup_ppcov_complex()
    # ppcov_complex_test()
    # setup_ppcov_simple()
    # ppcov_simple_test()
    # fac2real_test()
    # vario_test()
    # geostruct_test()
    # aniso_test()
    # struct_file_test()
    # covariance_matrix_test()