import statistics
import numpy as np
from scipy.spatial import distance as dist_eu
from skopt import dump, load
import inspect, re
from PIL import Image
import matplotlib.pyplot as plt
import os
from skopt.space.space import Real

def get_concat_h( im1, im2):
    """
        Concat two images as it follows:
        -    im1 = Image.open('Comparing Acquisition Function Mean.png')
        -    im2 = Image.open('Comparing Acquisition Function Mean 1x.png')
        -    get_concat_h(im1, im2).save('h.jpg')

        -PIL.Image module needed

        Parameters
        ----------
        im1 : First image

        im2 : Second image 

        Returns
        -------
        dst : im1 and im2 concatenation
            
    """    
    dst = Image.new('RGB', (im1.width + im2.width, im1.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst

def dict_to_list_of_list(dict):
    """
        Return a list of a given dictionary.

        Parameters
        ----------
        dict : a dictionary

        Returns
        -------
        list_of_list : A list of the values
                       of dict
            
    """ 
    list_of_list = []
    for element in dict:
        list_of_list.append( dict[element].bounds )
    return list_of_list

def list_to_dict(lista, dict):
    """
        Return a dictionary of a given list.
        The key of the dictionary are the same of dict.

        Parameters
        ----------
        lista : list

        dict : a dictionary

        Returns
        -------
        space : A dictionary with the value of list and the
                key of dict
            
    """ 
    space = {}
    i = 0
    for element in dict:
        space[element] = lista[i]#Real(low=lista[i], high=lista[i]+0.00000000000001)
        i = i+1
    return space

def random_generator( bounds, n , n_iter):
    """
        Return a list of n random numbers in the bounds
        repeat itself for n_iter iteration.
        Random numbers are generated with 
        uniform distribution
        -np.random.uniform module needed

        Parameters
        ----------
        bounds : A list of bound for the random numbers

        n : Number of random numbers for each iteration

        n_iter : Number of iterations

        Returns
        -------
        array : A list of n*n_iter random numbers 
                in the bounds
            
    """    
    array = []
    for i in range( n_iter ):
        array.append( [] )
    for i in range( n_iter ):
        for j in range( n ):
            array[i].append( [] )
    dimensione = len( bounds )
    for i in range( n_iter ):
        for j in range( n ):
            for d in range( dimensione ):
                array[i][j].append( np.random.uniform(low = bounds[d][0], 
                                                    high = bounds[d][1]) )
    return array

def funct_eval( funct, points):
    """
        Return a list of the evaluation of the points 
        in the function funct
        Build to work with random_generator()

        Parameters
        ----------
        funct : A function the return a single value

        points : A list of point

        Returns
        -------
        array : A list of evaluation
    """    
    array = []
    for i in range( len( points ) ):
        array.append( [] )
    for i in range( len( points ) ):
        for j in range( len( points[0] ) ):
            array[i].append( funct( points[i][j] ) )
    return array

def convergence_res( res):
    """
        Given a single element of a
        Bayesian_optimization return the 
        convergence of y

        Parameters
        ----------
        res : A single element of a 
            Bayesian_optimization result

        Returns
        -------
        val : A list with the best min seen for 
            each evaluation
    """    
    val = res.func_vals
    for i in range( len(val) ):
        if( i != 0 and val[i] > val[i-1] ):
            val[i] = val[i-1]
    return val
    
def early_condition( result, n_stop, n_random):
    """
        Compute the decision to stop or not.

        Parameters
        ----------
        result : `OptimizeResult`, scipy object
                The optimization as a OptimizeResult object.
        
        n_stop : Range of points without improvement

        n_random : Random starting point

        Returns
        -------
        decision : Return True if early stop condition has been reached
    """
    n_min_len = n_stop + n_random
    if len(result.func_vals) >= n_min_len:
        func_vals = convergence_res( result )
        worst = func_vals[ len(func_vals) - (n_stop) ]
        best = func_vals[-1]
        diff = worst - best
        if( diff == 0 ):
            return True

    return False

def iteration_without_improvement( result ):
    """
        Compute the decision to stop or not.

        Parameters
        ----------
        result : `OptimizeResult`, scipy object
                The optimization as a OptimizeResult object.
        
        n_stop : Range of points without improvement

        n_random : Random starting point

        Returns
        -------
        decision : Return True if early stop condition has been reached
    """
    cont = 0
    if( len(result) > 0 ):
        func_vals = convergence_res( result )
        last = func_vals[-1]
        cont = func_vals.count(last)
    
    return cont

def varname( p):
    """
        Return the name of the variabile p
        -inspect module needed
        -re module needed

        Parameters
        ----------
        p : variable with a name

        Returns
        -------
        m : Name of the variable p
            
    """    
    for line in inspect.getframeinfo(inspect.currentframe().f_back)[3]:
        m = re.search(r'\bvarname\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)', line)
        if m:
            return m.group(1)

def print_func_vals( list_of_res):
    """
        Print the function's values of a
        Bayesian_optimization result 

        Parameters
        ----------
        list_of_res : A Bayesian_optimization result

    """    
    for i in range( len(list_of_res) ):
        print( list_of_res[i].func_vals )

def print_x_iters( list_of_res):
    """
        Print the x iteration of a
        Bayesian_optimization result 

        Parameters
        ----------
        list_of_res : A Bayesian_optimization result

    """    
    for i in range( len(list_of_res) ):
        print( list_of_res[i].x_iters )

def median( list_of_res):
    """
        Given a Bayesian_optimization result 
        the median of the min y found
        -statistics module needed

        Parameters
        ----------
        list_of_res : A Bayesian_optimization result

        Returns
        -------
        val : The median of the min y found
    """    
    r = []
    for res in list_of_res:
        r.append( list(convergence_res(res)) )
    val = []
    for i in r:
        val.append( i[-1] )
    val = statistics.median( val )
    return val

def len_func_vals( list_of_res ):
    """
        Given a Bayesian_optimization result 
        return a list of func_vals lenght

        Parameters
        ----------
        list_of_res : A Bayesian_optimization result

        Returns
        -------
        lista : A list of the lenght with of the
                func_vals
    """  
    lista = []
    for i in list_of_res:
        lista.append( len( i.func_vals ) )
    return lista

def total_mean( list_of_res):
    """
        Given a Bayesian_optimization result 
        return a list of the mean with the other 
        tests runned 

        Parameters
        ----------
        list_of_res : A Bayesian_optimization result

        Returns
        -------
        media : A list of the mean with the other 
                tests runned
    """    
    r = []
    different_iteration = len( list_of_res )
    for res in list_of_res:
        r.append( list(convergence_res(res)) )
    a = []
    media = []
    max_len = max( len_func_vals( list_of_res ) ) 
    for i in range( max_len ):
        for j in range( different_iteration ):
            if( len(r[j]) > i ):
                a.append( r[j][i] )
        media.append( np.mean(a, dtype=np.float64) )
        a = []
    return media

def total_standard_deviation( list_of_res):
    """
        Given a Bayesian_optimization result 
        return a list of the standard deviation
        with the other tests runned 

        Parameters
        ----------
        list_of_res : A Bayesian_optimization result

        Returns
        -------
        dev : A list of the standard deviation
            with the other test runned
    """    
    r = []
    different_iteration = len( list_of_res )
    for res in list_of_res:
        r.append( list(convergence_res(res)) )
    a = []
    dev = []
    max_len = max( len_func_vals( list_of_res ) ) 
    for i in range( max_len ):
        for j in range( different_iteration ):
            if( len(r[j]) > i ):
                a.append( r[j][i] )
        dev.append( np.std(a, dtype=np.float64) )
        a = []
    return dev

def upper_standard_deviation( list_of_res):
    """
        Given a Bayesian_optimization result 
        return a list of the higher standard 
        deviation from the tests runned 

        Parameters
        ----------
        list_of_res : A Bayesian_optimization result

        Returns
        -------
        upper : A list of the higher standard 
                deviation with the other tests runned
    """
    media = total_mean(list_of_res)
    dev = total_standard_deviation(list_of_res)
    upper = []
    for i in range( len( media ) ):
        upper.append( media[i] + dev[i] ) 
    return upper

def lower_standard_deviation( list_of_res):
    """
        Given a Bayesian_optimization result 
        return a list of the lower standard 
        deviation from the tests runned 

        Parameters
        ----------
        list_of_res : A Bayesian_optimization result

        Returns
        -------
        lower : A list of the lower standard 
                deviation with the other tests runned
    """
    media = total_mean(list_of_res)
    dev = total_standard_deviation(list_of_res)
    lower = []
    for i in range( len( media ) ):
        lower.append( media[i] - dev[i] ) 
    return lower

def convergence_res_x( res, r_min):
    """
        Given a single element of a
        Bayesian_optimization and the argmin
        of the function return the convergence of x
        centred around the lowest distance 
        from the argmin
        -scipy.spatial.distance module needed


        Parameters
        ----------
        res : A single element of a 
            Bayesian_optimization result

        min : the argmin of the function in form 
            of a list as it follows:
            -[[-pi, 12.275], [pi, 2.275], [9.42478, 2.475] ]

        Returns
        -------
        distance : A list with the distance between 
            the best x seen for each evaluation
            and the argmin
    """    
    val = res.x_iters
    distance = []
    if( len(r_min) == 1 ):
        for i in range( len(val) ):
            if( i != 0 and dist_eu.euclidean(val[i],r_min) > distance[i-1] ):
                distance.append( distance[i-1] )
            else:
                distance.append( dist_eu.euclidean(val[i],r_min) )
        return distance
    else:
        distance_all_min = []
        for i in range( len(val) ):
            for j in range( len(r_min) ):
                distance_all_min.append( dist_eu.euclidean(val[i],r_min[j]) )
            min_distance = min( distance_all_min )
            if( i != 0 and min_distance > distance[i-1] ):
                distance.append( distance[i-1] )
            else:
                distance.append( min_distance )
            distance_all_min = []
        return distance

def total_mean_x( list_of_res, min):
    """
        Given a Bayesian_optimization result
        and the argmin of the function return 
        the mean of x centred around the lowest 
        distance from the argmin

        Parameters
        ----------
        res : A Bayesian_optimization result

        min : the argmin of the function in form 
            of a list as it follows:
            -[[-pi, 12.275], [pi, 2.275], [9.42478, 2.475] ]

        Returns
        -------
        media : A list with the mean of the distance 
                between the best x seen for each 
                evaluation and the argmin
    """
    r = []
    different_iteration = len( list_of_res )
    for res in list_of_res:
        r.append( list(convergence_res_x(res, min)) )
    a = []
    media = []
    for i in range( len( list_of_res[0].func_vals ) ):
        for j in range( different_iteration ):
            a.append( r[j][i] )
        media.append( np.mean(a, dtype=np.float64) )
        a = []
    return media

def total_standard_deviation_x( list_of_res, min):
    """
        Given a Bayesian_optimization result
        and the argmin of the function return 
        the standard deviation of x centred around 
        the lowest distance from the argmin

        Parameters
        ----------
        res : A Bayesian_optimization result

        min : the argmin of the function in form 
            of a list as it follows:
            -[[-pi, 12.275], [pi, 2.275], [9.42478, 2.475] ]

        Returns
        -------
        dev : A list with the standard deviation of the 
            distance between the best x seen for each 
            evaluation and the argmin
    """
    r = []
    different_iteration = len( list_of_res )
    for res in list_of_res:
        r.append( list(convergence_res_x(res, min)) )
    a = []
    dev = []
    for i in range( len( list_of_res[0].func_vals ) ):
        for j in range( different_iteration ):
            a.append( r[j][i] )
        dev.append( np.std(a, dtype=np.float64) )
        a = []
    return dev

def upper_standard_deviation_x( list_of_res, min):
    """
        Given a Bayesian_optimization result
        and the argmin of the function return 
        higher standard deviation from the tests 
        runned in x

        Parameters
        ----------
        res : A Bayesian_optimization result

        min : the argmin of the function in form 
            of a list as it follows:
            -[[-pi, 12.275], [pi, 2.275], [9.42478, 2.475] ]

        Returns
        -------
        upper : A list with the higher standard deviation 
                from the tests runned in x
    """
    media = total_mean_x(list_of_res, min)
    dev = total_standard_deviation_x(list_of_res, min)
    upper = []
    for i in range( len( media ) ):
        upper.append( media[i] + dev[i] ) 
    return upper

def lower_standard_deviation_x( list_of_res, min):
    """
        Given a Bayesian_optimization result
        and the argmin of the function return 
        lower standard deviation from the tests 
        runned in x

        Parameters
        ----------
        res : A Bayesian_optimization result

        min : the argmin of the function in form 
            of a list as it follows:
            -[[-pi, 12.275], [pi, 2.275], [9.42478, 2.475] ]

        Returns
        -------
        lower : A list with the lower standard deviation 
                from the tests runned in x
    """
    media = total_mean_x(list_of_res, min)
    dev = total_standard_deviation_x(list_of_res, min)
    lower = []
    for i in range( len( media ) ):
        lower.append( media[i] - dev[i] ) 
    return lower

def my_key_fun( res ):
    """
        Sort key for fun_min function
    """    
    return res.fun

def fun_min( list_of_res ):
    """
        Return the min of a list of BO
    """    
    min_res = min(list_of_res, key = my_key_fun )
    return [ min_res.fun, min_res.x ]

def tabella( list_of_list_of_res ):
    """
        Given a list of Bayesian_optimization results
        return a list with name, mean, median, 
        standard deviation and min result founded
        for each Bayesian_optimization result

        Parameters
        ----------
        list_of_list_of_res : A list of Bayesian_optimization 
                            results 

        Returns
        -------
        lista : A list with name, mean, median, 
                standard deviation and min result founded
                for each Bayesian_optimization result
    """    
    lista = []
    different_iteration = len( list_of_list_of_res[0] )
    for i in list_of_list_of_res:
        fun_media = []
        for it in range( different_iteration ):
            fun_media.append( i[0][it].fun )
        
        lista.append( [ i[1], np.mean(fun_media, dtype=np.float64) , median( i[0] ), np.std(fun_media, dtype=np.float64), fun_min( i[0] ) ] )
        # nome, media, mediana, std, [.fun min, .x min]
    return lista

def my_key_sort( list_with_name):
    """
        Sort key for top_5 funcion
    """    
    return list_with_name[0]

def top_5( list_of_list_of_res ):
    """
        Given a list of Bayesian_optimization results
        find out the best 5 result confronting the 
        best mean result

        Parameters
        ----------
        list_of_list_of_res : A list of Bayesian_optimization 
                            results 

        Returns
        -------
        list_medie : A list of each .pkl file's name 
                    just saved
                    -    list_of_list_of_res = [[res_BO_1,"name_1", 1], [res_BO_2,"name_2", 2],etc.]
    """    
    list_medie = []
    for i in list_of_list_of_res:
        list_medie.append( [ total_mean( i[0] ), i[1], i[2] ] )
    list_medie.sort( key = my_key_sort )
    list_medie = list_medie[:5]
    return list_medie

def plot_bayesian_optimization( list_of_res, name_plot = "plot_BO",
                                log_scale = False, path = None):
    """
        Save a plot of the result of a Bayesian_optimization 
        considering mean and standard deviation

        Parameters
        ----------
        list_of_res : A Bayesian_optimization result

        name_plot : The name of the file you want to 
                    give to the plot

    """    
    media = total_mean( list_of_res )
    array = [ i for i in range( len( media ) ) ]
    plt.plot(array, media, color='blue', label= "res" )

    plt.fill_between(array, 
                    lower_standard_deviation( list_of_res ), 
                    upper_standard_deviation( list_of_res ),
                    color='blue', alpha=0.2)

    lista_early_stop = len_func_vals( list_of_res )
    max_list = max( lista_early_stop )
    flag = True
    for i in lista_early_stop:
        if( i != max_list ):
            if( flag ):
                plt.axvline( x=(i-1), color='red', label= "early stop")
                flag = False #In this way it doesn't generate too many label
            else:
                plt.axvline( x=(i-1), color='red')

    if( log_scale ):
        plt.yscale('log')

    x_int = range(0, array[-1]+1)
    plt.xticks(x_int)

    plt.ylabel('min f(x) after n calls')
    plt.xlabel('Number of calls n')
    plt.legend(loc='best')
    plt.tight_layout()
    plt.grid(True)
    if( path == None ):
        plt.savefig( name_plot ) #save in the current working directory
    else:
        if( path[-1] != '/' ):
                path = path + "/"
        current_dir = os.getcwd() #current working directory
        os.chdir( path ) #change directory
        plt.savefig( name_plot )
        os.chdir( current_dir ) #reset directory to original

    plt.clf()

def dump_BO( list_of_res, stringa = 'result', path = None ):
    """
        Dump (save) the Bayesian_optimization result

        Parameters
        ----------
        list_of_res : A result of a Bayesian_optimization
                    run
        stringa : Name of the log file saved in .pkl 
                format after the run of the function

        Returns
        -------
        lista_dump : A list of each .pkl file's name 
                    just saved 
    """
    lista_dump = []
    if( path == None ):
        for n in range( len( list_of_res ) ):
            name_file = stringa + str( n ) + '.pkl'
            dump( list_of_res[n] , name_file)
            lista_dump.append( name_file ) #save in the current working directory        
    else:
        current_dir = os.getcwd() #current working directory
        os.chdir( path ) #change directory
        if( path[-1] != '/' ):
                path = path + "/"

        for n in range( len( list_of_res ) ):
            name_file = stringa + str( n ) + '.pkl'
            dump( list_of_res[n] , name_file)

            lista_dump.append( path + name_file )

        os.chdir( current_dir ) #reset directory to original
        
    return lista_dump

def load_BO( lista_dump ):
    """
        Load a list of pkl files, it should have the 
        list returned from dump_BO to work 
        properly, as it follows:
        -   lista_dump = dump_BO( res_gp_rosenbrock )
        -   res_loaded = load_BO( lista_dump )

        Parameters
        ----------
        lista_dump : A list of .pkl files

        Returns
        -------
        lista_res_loaded : A Bayesian_optimization result
    """
    lista_res_loaded = []
    for n in range( len( lista_dump ) ):
        res_loaded = load( lista_dump[n] )
        lista_res_loaded.append( res_loaded )
    return lista_res_loaded
    