#!/usr/bin/env python

import pytest
from .critical_path_finder import CriticalPath, RunBeforeSaveException, MissingInputsException, NodeWeightsDuplicateValues
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
def graph_cycle():
    return CriticalPath._get_digraph_from_tuples([(1,2), (2,3), (3,1)])       

@pytest.fixture
def node_weights_map_complex():
    return {1:1, 2:2, 3:3, 4:4, 5:5}

@pytest.fixture
def graph_complex():
    return CriticalPath._get_digraph_from_tuples([(1,2), (2,3), (3,4), (4,5), (1,5)]) 



def test_critical_path(node_weights_map, graph, node_weights_map_complex, graph_complex):
    cp_simple = CriticalPath(node_weights_map=node_weights_map, graph=graph)
    assert cp_simple.find() == {(1,2): 1, (2,3): 2}
    assert cp_simple.validate() == None
    
    cp_complex = CriticalPath(node_weights_map=node_weights_map_complex, graph=graph_complex)
    assert cp_complex.validate() == None
    assert cp_complex.find() == {(1,2): 1, (2,3): 2, (3, 4): 3, (4, 5): 4}

    with pytest.raises(MissingInputsException):
        CriticalPath().validate()

    with pytest.raises(MissingInputsException):
        CriticalPath().find()
    
def test_critical_path_with_cycle(node_weights_map, graph_cycle):
    cp_cycle =  CriticalPath(node_weights_map=node_weights_map, graph=graph_cycle)
    assert cp_cycle.validate() == None
    
    with pytest.raises(NetworkXUnfeasible):
        cp_cycle.find()


def test_edge_weights(node_weights_map, graph):
    cp_complex = CriticalPath(node_weights_map=node_weights_map, graph=graph)
    assert cp_complex.edge_weights == {(1, 2): 1, (2, 3): 2}


def test_get_edges_from_ordered_list_of_nodes():
    nodes = [1, 2, 3]
    expected = [(1,2), (2,3)]
    result = CriticalPath._get_edges_from_ordered_list_of_nodes(nodes=nodes)
    assert expected == result


@pytest.mark.skip(reason="Needs handling to read from filesystem")
def test_load_graph():
    pass


@pytest.mark.skip(reason="Needs handling to read from filesystem")
def test_load_weights():
    # TODO: Positive test

    # TODO: Negative test
    with pytest.raises(NodeWeightsDuplicateValues):
        pass
    pass


@pytest.mark.skip(reason="Needs handling for image write to filesystem")
def test_save_image(node_weights_map, graph, tmpdir):
    path = tmpdir.join("some/path")

    with pytest.raises(MissingInputsException):
        CriticalPath().save_image(fname=path)

    # https://docs.pytest.org/en/6.2.x/tmpdir.html
    with pytest.raises(RunBeforeSaveException):
        CriticalPath(node_weights_map=node_weights_map, graph=graph).save_image(fname=path.strpath)

    cp = CriticalPath(node_weights_map=node_weights_map, graph=graph)
    cp.find()
    assert cp.save_image(fname=path.strpath) == None
