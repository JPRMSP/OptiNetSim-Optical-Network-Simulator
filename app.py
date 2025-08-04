import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import random

# ----------------------------
# Network Creation Functions
# ----------------------------
def create_topology(nodes, topology_type):
    G = nx.Graph()
    G.add_nodes_from(range(1, nodes + 1))

    if topology_type == "Ring":
        for i in range(1, nodes + 1):
            G.add_edge(i, (i % nodes) + 1, wavelength=None)

    elif topology_type == "Mesh":
        for i in range(1, nodes + 1):
            for j in range(i + 1, nodes + 1):
                G.add_edge(i, j, wavelength=None)

    elif topology_type == "Star":
        for i in range(2, nodes + 1):
            G.add_edge(1, i, wavelength=None)

    elif topology_type == "PON":
        # Central OLT (node 1) to all ONUs
        for i in range(2, nodes + 1):
            G.add_edge(1, i, wavelength=None)

    elif topology_type == "WRPON":
        # OLT connected to wavelength routers, then ONUs
        middle = nodes // 2
        for i in range(2, middle + 2):
            G.add_edge(1, i, wavelength=None)
        for i in range(2, middle + 2):
            for j in range(middle + 2, nodes + 1):
                G.add_edge(i, j, wavelength=None)

    elif topology_type == "Broadcast Select PON":
        # OLT broadcasting to all
        for i in range(2, nodes + 1):
            G.add_edge(1, i, wavelength=None)

    return G


def assign_wavelengths(G, wavelengths):
    for u, v in G.edges():
        G[u][v]['wavelength'] = random.choice(wavelengths)
    return G


# ----------------------------
# QoS Metrics
# ----------------------------
def qos_metrics(traffic_load, hops, wavelength_conversion):
    latency = hops * (0.5 if wavelength_conversion else 1)
    throughput = max(0, 100 - traffic_load * 2)
    return latency, throughput


# ----------------------------
# Node Failure Simulation
# ----------------------------
def simulate_node_failure(G, failed_node):
    if failed_node in G.nodes():
        G.remove_node(failed_node)
    return G


# ----------------------------
# Network Visualization
# ----------------------------
def plot_network(G):
    pos = nx.spring_layout(G, seed=42)
    edge_colors = [G[u][v]['wavelength'] for u, v in G.edges()]

    fig = go.Figure()

    # Draw edges
    for edge, color in zip(G.edges(), edge_colors):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        fig.add_trace(go.Scatter(
            x=[x0, x1], y=[y0, y1],
            mode='lines',
            line=dict(color='blue' if color is None else color, width=2),
            hoverinfo='none'
        ))

    # Draw nodes
    fig.add_trace(go.Scatter(
        x=[pos[node][0] for node in G.nodes()],
        y=[pos[node][1] for node in G.nodes()],
        mode='markers+text',
        text=list(G.nodes()),
        textposition="top center",
        marker=dict(size=15, color='lightblue', line=dict(width=2, color='black'))
    ))

    fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=0, b=0))
    return fig


# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(page_title="OptiNetSim", layout="wide")
st.title("💡 OptiNetSim: Optical Network Simulator")

col1, col2 = st.columns(2)

with col1:
    nodes = st.slider("Number of Nodes", 3, 15, 6)
    topology_type = st.selectbox("Select Topology", [
        "Ring", "Mesh", "Star", "PON", "WRPON", "Broadcast Select PON"
    ])
    traffic_load = st.slider("Traffic Load (%)", 0, 100, 30)
    wavelength_conversion = st.checkbox("Enable Wavelength Conversion", True)
    failed_node = st.number_input("Simulate Node Failure (Enter Node No.)", min_value=0, max_value=nodes, value=0)

with col2:
    wavelengths = st.multiselect("Available Wavelengths", ["red", "green", "blue", "orange"], default=["red", "green", "blue"])
    hops = st.slider("Average Hops in Path", 1, 10, 4)

# Create and simulate
G = create_topology(nodes, topology_type)
G = assign_wavelengths(G, wavelengths)

if failed_node != 0:
    G = simulate_node_failure(G, failed_node)

latency, throughput = qos_metrics(traffic_load, hops, wavelength_conversion)

# Display results
st.subheader("Network Topology")
st.plotly_chart(plot_network(G), use_container_width=True)

st.subheader("QoS Metrics")
st.write(f"**Latency:** {latency} ms")
st.write(f"**Throughput:** {throughput} %")

st.info("Adjust the parameters on the left to see real-time changes in the optical network simulation.")
