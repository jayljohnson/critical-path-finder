#!/usr/bin/env python

import sys
from io import BytesIO
import pytest
from .critical_path_finder import CriticalPath, RunBeforeSaveException, MissingInputsException, NodeWeightsDuplicateValues, MustBeDirectedAcyclicGraph
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
    return [(1,2), (2,3), (3,1)]

@pytest.fixture
def node_weights_map_complex():
    return {1:1, 2:2, 3:3, 4:4, 5:5}

@pytest.fixture
def graph_complex():
    return CriticalPath._get_digraph_from_tuples([(1,2), (2,3), (3,4), (4,5), (1,5)])

@pytest.fixture
def dot_digraph():
    graph = """
digraph G { 
  t1 -> t2 -> t3;
  t2 -> t4;
  t3 -> t5;
  t4 -> t6;
  t5 -> t6;  
  }
"""
    return graph

def test_get_digraph_from_tuples_with_cycle(graph_cycle):
    
    with pytest.raises(MustBeDirectedAcyclicGraph):
        G = CriticalPath._get_digraph_from_tuples(graph_cycle)

def test_get_edge_tuples_from_dotviz(dot_digraph):

    from io import StringIO

    expected = [
        ('t1', 't2'),
        ('t2', 't3'),
        ('t2', 't4'),
        ('t3', 't5'),
        ('t4', 't6'),
        ('t5', 't6')
        ]
    with StringIO(dot_digraph) as g:
        result = CriticalPath._get_edge_tuples_from_dotviz(g)
    assert result == expected

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

def test_edge_weights(node_weights_map, graph):
    cp_complex = CriticalPath(node_weights_map=node_weights_map, graph=graph)
    assert cp_complex.edge_weights == {(1, 2): 1, (2, 3): 2}

def test_get_edges_from_ordered_list_of_nodes():
    nodes = [1, 2, 3]
    expected = [(1,2), (2,3)]
    result = CriticalPath._get_edges_from_ordered_list_of_nodes(nodes=nodes)
    assert expected == result

@pytest.mark.skip(reason="Needs handling to read from filesystem")
def test_load_weights():
    # TODO: Positive test

    # TODO: Negative test
    with pytest.raises(NodeWeightsDuplicateValues):
        pass
    pass

def test_save_image(node_weights_map, graph):
    
    with BytesIO() as path:

        with pytest.raises(MissingInputsException):
            CriticalPath().save_image(fname=path)

        with pytest.raises(RunBeforeSaveException):
            CriticalPath(node_weights_map=node_weights_map, graph=graph).save_image(fname=path)

        cp = CriticalPath(node_weights_map=node_weights_map, graph=graph)
        cp.find()
        fileobj = cp.save_image(fname=path)
        assert type(fileobj) == BytesIO
        # To identify if file generation logic changed, resulting in different file size. 
        # If image file still looks okay update the `expected_size` value to the new value
        expected_size = 11376
        assert sys.getsizeof(fileobj) == expected_size
