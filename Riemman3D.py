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
mpmath.mp.dps = 20

def compute_zeta_surface(sigma_min, sigma_max, t_max, num_points_sigma, num_points_t):
    """Compute |zeta(s)| values for the given range, avoiding poles"""
    # Adjust to avoid σ = 1.0 exactly
    sigma_min_adj = max(0.01, sigma_min)
    sigma_max_adj = min(0.99, sigma_max) if sigma_max >= 1.0 else sigma_max
    
    sigma_values = np.linspace(sigma_min_adj, sigma_max_adj, num_points_sigma)
    t_values = np.linspace(0.1, t_max, num_points_t)  # Avoid t=0
    
    X, Y = np.meshgrid(sigma_values, t_values)
    Z = np.zeros_like(X, dtype=float)
    
    progress_text = f"Computing zeta values for σ=[{sigma_min_adj:.2f}, {sigma_max_adj:.2f}], t=[0.1, {t_max}]..."
    progress_bar = st.progress(0, text=progress_text)
    
    total_points = len(t_values) * len(sigma_values)
    completed_points = 0
    
    for i in range(len(t_values)):
        for j in range(len(sigma_values)):
            s = complex(X[i, j], Y[i, j])
            try:
                Z[i, j] = abs(mpmath.zeta(s))
            except:
                Z[i, j] = np.nan  # Handle any computation errors
            
            completed_points += 1
            if completed_points % 100 == 0:  # Update progress every 100 points
                progress_bar.progress(completed_points / total_points, text=progress_text)
    
    progress_bar.empty()  # Remove progress bar when done
    return X, Y, Z, sigma_values, t_values

def create_zeta_plot(sigma_min, sigma_max, t_max, num_points_sigma=60, num_points_t=80):
    """Create interactive 3D plot of |zeta(s)|"""
    X, Y, Z, sigma_values, t_values = compute_zeta_surface(sigma_min, sigma_max, t_max, 
                                                          num_points_sigma, num_points_t)
    
    # Create surface plot
    surface = go.Surface(
        x=X, y=Y, z=Z,
        colorscale='Viridis',
        opacity=0.85,
        name='|ζ(σ + it)|',
        colorbar=dict(title="|ζ(s)|", titleside="right"),
        hovertemplate='<b>σ</b>: %{x:.3f}<br><b>t</b>: %{y:.3f}<br><b>|ζ(s)|</b>: %{z:.6f}<extra></extra>'
    )
    
    # Create critical line if it's in the range
    critical_sigma = 0.5
    if sigma_min <= 0.5 <= sigma_max:
        critical_line_t = np.linspace(0.1, t_max, 100)
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
        critical_line = go.Scatter3d(x=[], y=[], z=[], name='Critical Line (σ=0.5)')
    
    # Create figure
    fig = go.Figure(data=[surface, critical_line])
    
    fig.update_layout(
        title=f'3D Plot of |ζ(s)| for σ ∈ [{sigma_min:.2f}, {sigma_max:.2f}], t ∈ [0.1, {t_max}]',
        scene=dict(
            xaxis_title='Real Part (σ)',
            yaxis_title='Imaginary Part (t)',
            zaxis_title='|ζ(s)|',
            zaxis_type='log',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
        ),
        width=1000,
        height=700
    )
    
    return fig

def main():
    st.title("🧮 Riemann Zeta Function 3D Explorer")
    st.markdown("""
    Visualize the absolute value of the Riemann Zeta Function |ζ(s)| in 3D, where **s = σ + it** is a complex number.
    The **Riemann Hypothesis** states that all non-trivial zeros lie on the **critical line σ = 0.5**.
    """)
    
    # Create sidebar for controls
    with st.sidebar:
        st.header("Controls")
        
        st.subheader("Real Part (σ) Range")
        sigma_min = st.slider("σ minimum", 0.1, 0.9, 0.4, 0.1, help="Minimum value for the real part")
        sigma_max = st.slider("σ maximum", 0.2, 0.9, 0.6, 0.1, help="Maximum value for the real part")
        
        st.subheader("Imaginary Part (t) Range")
        t_max = st.slider("t maximum", 5.0, 50.0, 30.0, 5.0, help="Maximum value for the imaginary part")
        
        st.subheader("Animation")
        animate = st.checkbox("Create animation", False, help="Animate through different t values")
        
        if animate:
            animation_speed = st.slider("Animation speed", 1, 10, 3)
            num_frames = st.slider("Number of frames", 5, 30, 10)
        
        st.subheader("Resolution")
        resolution = st.slider("Grid resolution", 30, 100, 60, help="Higher = more detailed but slower")
        
        if st.button("Compute Plot", type="primary"):
            st.session_state.compute_plot = True
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if 'compute_plot' in st.session_state and st.session_state.compute_plot:
            with st.spinner("Generating 3D plot..."):
                fig = create_zeta_plot(sigma_min, sigma_max, t_max, resolution, resolution)
                st.plotly_chart(fig, use_container_width=True)
                
                # Show some information about the plot
                st.info(f"""
                **Plot Details:**
                - **σ range:** [{sigma_min:.2f}, {sigma_max:.2f}]
                - **t range:** [0.1, {t_max:.1f}]
                - **Critical line:** σ = 0.5 (shown in red)
                - **Zeros:** Points where |ζ(s)| ≈ 0 (deep purple valleys)
                """)
        
        else:
            st.info("👆 Adjust the parameters in the sidebar and click 'Compute Plot' to generate the 3D visualization.")
    
    with col2:
        st.subheader("About the Riemann Hypothesis")
        st.markdown("""
        The Riemann Zeta Function is defined as:
        
        $$
        \\zeta(s) = \\sum_{n=1}^{\\infty} \\frac{1}{n^s}
        $$
        
        for Re(s) > 1, and can be analytically continued to the entire complex plane.
        
        **The Riemann Hypothesis** states that all non-trivial zeros of ζ(s) have real part equal to **0.5**.
        
        This visualization shows |ζ(s)| as a surface. The deep valleys that touch zero represent the zeros of the function.
        """)
        
        st.subheader("How to Use")
        st.markdown("""
        1. Adjust the σ and t ranges in the sidebar
        2. Click 'Compute Plot' to generate the 3D surface
        3. Rotate the plot by dragging with your mouse
        4. Zoom in/out using the scroll wheel
        5. Hover over points to see exact values
        """)
    
    # Animation section
    if animate and 'compute_plot' in st.session_state and st.session_state.compute_plot:
        st.subheader("🎬 Animation")
        st.warning("Note: Animation may take a while to compute for high resolutions.")
        
        animation_placeholder = st.empty()
        t_values = np.linspace(5, t_max, num_frames)
        
        for i, current_t_max in enumerate(t_values):
            with animation_placeholder.container():
                st.write(f"Frame {i+1}/{num_frames}: t_max = {current_t_max:.1f}")
                fig_anim = create_zeta_plot(sigma_min, sigma_max, current_t_max, 40, 40)  # Lower res for animation
                st.plotly_chart(fig_anim, use_container_width=True)
                time.sleep(1/animation_speed)

if __name__ == "__main__":
    main()
