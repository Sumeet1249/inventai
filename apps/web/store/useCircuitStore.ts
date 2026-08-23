import { create } from 'zustand';
import {
  Connection,
  Edge,
  EdgeChange,
  Node,
  NodeChange,
  addEdge,
  OnNodesChange,
  OnEdgesChange,
  OnConnect,
  applyNodeChanges,
  applyEdgeChanges,
} from '@xyflow/react';

export type ComponentNodeData = {
  label: string;
  value: string;
  component_id: string;
};

export type CircuitNode = Node<ComponentNodeData>;

interface CircuitState {
  nodes: CircuitNode[];
  edges: Edge[];
  onNodesChange: OnNodesChange<CircuitNode>;
  onEdgesChange: OnEdgesChange;
  onConnect: OnConnect;
  addNode: (node: CircuitNode) => void;
  setNodes: (nodes: CircuitNode[]) => void;
  setEdges: (edges: Edge[]) => void;
}

export const useCircuitStore = create<CircuitState>((set, get) => ({
  nodes: [],
  edges: [],
  onNodesChange: (changes: NodeChange<CircuitNode>[]) => {
    set({
      nodes: applyNodeChanges(changes, get().nodes),
    });
  },
  onEdgesChange: (changes: EdgeChange[]) => {
    set({
      edges: applyEdgeChanges(changes, get().edges),
    });
  },
  onConnect: (connection: Connection) => {
    set({
      edges: addEdge(connection, get().edges),
    });
  },
  addNode: (node: CircuitNode) => {
    set({ nodes: [...get().nodes, node] });
  },
  setNodes: (nodes: CircuitNode[]) => {
    set({ nodes });
  },
  setEdges: (edges: Edge[]) => {
    set({ edges });
  },
}));
