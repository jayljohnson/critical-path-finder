import pytest
from critical_path.critical_path import CriticalPath, MissingInputsException, RunBeforeSaveException
from networkx.exception import NetworkXUnfeasible
from networkx import DiGraph


def test__get_digraph_from_tuples():
    assert type(CriticalPath._get_digraph_from_tuples([(1,2), (2,3)])) == DiGraph

@pytest.fixture
def node_weights_map():
    return {1:1, 2:2, 3:3}

@pytest.fixture
def graph():
    return CriticalPath._get_digraph_from_tuples([(1,2), (2,3)])

@pytest.fixture
def node_weights_map_complex():
    return {1:1, 2:2, 3:3, 4:4, 5:5}

@pytest.fixture
def graph_complex():
    return CriticalPath._get_digraph_from_tuples([(1,2), (2,3), (3,4), (4,5), (1,5)]) 

@pytest.fixture
def graph_cycle():
    return CriticalPath._get_digraph_from_tuples([(1,2), (2,3), (3,4), (4,5), (5,1)])       


def test_critical_path(node_weights_map, graph, node_weights_map_complex, graph_complex, graph_cycle):
    cp_simple = CriticalPath(node_weights_map=node_weights_map, graph=graph)
    assert cp_simple.run() == {(1,2): 1, (2,3): 2}
    assert cp_simple.validate() == None
    
    cp_complex = CriticalPath(node_weights_map=node_weights_map_complex, graph=graph_complex)
    assert cp_complex.validate() == None
    assert cp_complex.run() == {(1,2): 1, (2,3): 2, (3, 4): 3, (4, 5): 4}

    with pytest.raises(MissingInputsException):
        CriticalPath().validate()

    with pytest.raises(MissingInputsException):
        CriticalPath().run()
    
def test_critical_path_with_cycle(node_weights_map_complex, graph_cycle):
    cp_cycle =  CriticalPath(node_weights_map=node_weights_map_complex, graph=graph_cycle)
    assert cp_cycle.validate() == None
    
    with pytest.raises(NetworkXUnfeasible):
        cp_cycle.run()


def test_edge_weights():
    pass


def test_load_graph():
    pass


def test_load_weights():
    pass


@pytest.mark.skip(reason="Needs handling for image write to filesystem")
def test_save_image(node_weights_map, graph, tmpdir):
    path = tmpdir.join("some/path")

    with pytest.raises(MissingInputsException):
        CriticalPath().save_image(path=path)

    # https://docs.pytest.org/en/6.2.x/tmpdir.html
    with pytest.raises(RunBeforeSaveException):
        CriticalPath(node_weights_map=node_weights_map, graph=graph).save_image(path=path.strpath)

    cp = CriticalPath(node_weights_map=node_weights_map, graph=graph)
    cp.run()
    assert cp.save_image(path=path.strpath) == None

def test_get_edges_from_ordered_list_of_nodes():
    pass