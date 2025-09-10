import streamlit as st
import plotly.graph_objects as go
import numpy as np
import mpmath
import time

# Set page config
st.set_page_config(
    page_title="Riemann Zeta Function 3D Explorer",
    page_icon="🧮",
    layout="wide"
)

# Set precision for mpmath
mpmath.mp.dps = 15

def compute_zeta_surface(sigma_min, sigma_max, t_max, num_points):
    """Compute |zeta(s)| values for the given range, avoiding poles"""
    # Adjust to avoid σ = 1.0 exactly
    sigma_min_adj = max(0.01, sigma_min)
    sigma_max_adj = min(0.99, sigma_max)
    
    sigma_values = np.linspace(sigma_min_adj, sigma_max_adj, num_points)
    t_values = np.linspace(0.1, t_max, num_points)
    
    X, Y = np.meshgrid(sigma_values, t_values)
    Z = np.zeros_like(X, dtype=float)
    
    progress_bar = st.progress(0, text="Computing zeta values...")
    total_points = len(t_values) * len(sigma_values)
    
    for i in range(len(t_values)):
        for j in range(len(sigma_values)):
            s = complex(X[i, j], Y[i, j])
            try:
                Z[i, j] = abs(mpmath.zeta(s))
            except:
                Z[i, j] = np.nan
            
            if (i * len(sigma_values) + j) % 100 == 0:
                progress = (i * len(sigma_values) + j) / total_points
                progress_bar.progress(progress, text=f"Computing... {progress*100:.1f}%")
    
    progress_bar.empty()
    return X, Y, Z

def create_zeta_plot(X, Y, Z, sigma_min, sigma_max, t_max):
    """Create interactive 3D plot of |zeta(s)|"""
    # Create surface plot with simplified colorbar
    surface = go.Surface(
        x=X,
        y=Y, 
        z=Z,
        colorscale='Viridis',
        opacity=0.8,
        name='|ζ(σ + it)|',
        hovertemplate='<b>σ</b>: %{x:.3f}<br><b>t</b>: %{y:.3f}<br><b>|ζ(s)|</b>: %{z:.6f}<extra></extra>'
    )
    
    # Create critical line
    critical_sigma = 0.5
    if sigma_min <= 0.5 <= sigma_max:
        critical_line_t = np.linspace(0.1, t_max, 50)
        critical_line_z = np.zeros_like(critical_line_t)
        
        for i, t in enumerate(critical_line_t):
            s = complex(critical_sigma, t)
            critical_line_z[i] = abs(mpmath.zeta(s))
        
        critical_line = go.Scatter3d(
            x=[critical_sigma] * len(critical_line_t),
            y=critical_line_t,
            z=critical_line_z,
            mode='lines',
            line=dict(color='red', width=4),
            name='Critical Line (σ=0.5)'
        )
    else:
        critical_line = go.Scatter3d(x=[], y=[], z=[], name='Critical Line')
    
    # Create figure
    fig = go.Figure(data=[surface, critical_line])
    
    fig.update_layout(
        title=f'|ζ(s)| for σ ∈ [{sigma_min:.2f}, {sigma_max:.2f}], t ∈ [0.1, {t_max}]',
        scene=dict(
            xaxis_title='Real Part (σ)',
            yaxis_title='Imaginary Part (t)',
            zaxis_title='|ζ(s)|',
            zaxis_type='log',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
        ),
        width=800,
        height=600
    )
    
    return fig

def main():
    st.title("🧮 Riemann Zeta Function 3D Explorer")
    st.markdown("""
    Visualize the absolute value of the Riemann Zeta Function |ζ(s)| where **s = σ + it**.
    The **Riemann Hypothesis** states that all non-trivial zeros lie on the **critical line σ = 0.5**.
    """)
    
    # Sidebar controls
    with st.sidebar:
        st.header("Controls")
        
        col1, col2 = st.columns(2)
        with col1:
            sigma_min = st.slider("σ min", 0.1, 0.9, 0.4, 0.05)
        with col2:
            sigma_max = st.slider("σ max", 0.2, 0.9, 0.6, 0.05)
        
        t_max = st.slider("t max", 10.0, 50.0, 30.0, 5.0)
        resolution = st.slider("Resolution", 30, 80, 50, 10)
        
        compute = st.button("Generate Plot", type="primary")
    
    # Main content
    if compute:
        with st.spinner("Computing zeta function values..."):
            X, Y, Z = compute_zeta_surface(sigma_min, sigma_max, t_max, resolution)
            
            st.success("Computation complete! Displaying 3D plot...")
            fig = create_zeta_plot(X, Y, Z, sigma_min, sigma_max, t_max)
            st.plotly_chart(fig, use_container_width=True)
            
            # Show info
            st.info(f"""
            **Plot Information:**
            - **σ range:** {sigma_min:.2f} to {sigma_max:.2f}
            - **t range:** 0.1 to {t_max:.1f}
            - **Resolution:** {resolution}×{resolution} points
            - **Critical line:** σ = 0.5 (red line)
            - **Deep valleys** indicate zeros of ζ(s)
            """)
    
    # Educational content
    st.sidebar.markdown("---")
    st.sidebar.header("About")
    st.sidebar.markdown("""
    The Riemann Zeta Function:
    $$
    \\zeta(s) = \\sum_{n=1}^{\\infty} \\frac{1}{n^s}
    $$
    for Re(s) > 1, with analytic continuation to ℂ.
    
    **Riemann Hypothesis:** All non-trivial zeros have Re(s) = 1/2.
    """)
    
    # Instructions
    st.sidebar.header("Instructions")
    st.sidebar.markdown("""
    1. Adjust parameters in sidebar
    2. Click 'Generate Plot'
    3. Rotate: Click + drag
    4. Zoom: Scroll wheel
    5. Pan: Right-click + drag
    """)

if __name__ == "__main__":
    main()
