import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

def plot_daily_utilization(daily_data):
    """
    Create a visualization of machine utilization throughout a day.
    
    Args:
        daily_data (list): List of hourly data entries for a day
        
    Returns:
        plotly.graph_objects.Figure: The plotly figure object
    """
    # Sort data by hour
    daily_data.sort(key=lambda x: x['hour'])
    
    # Prepare data for plotting
    hours = []
    machine_utilization = {f"Machine {i}": [] for i in range(9, 21)}
    
    for data in daily_data:
        hour = data['hour']
        hours.append(f"{hour}:00")
        
        # Add utilization data for each machine
        for machine_number in range(9, 21):
            machine_name = f"Machine {machine_number}"
            
            if machine_name in data['machines']:
                machine_utilization[machine_name].append(data['machines'][machine_name]['utilization'])
            else:
                machine_utilization[machine_name].append(None)
    
    # Create figure
    fig = go.Figure()
    
    # Add traces for each machine
    for machine_number in range(9, 21):
        machine_name = f"Machine {machine_number}"
        
        # Filter out None values
        valid_indices = [i for i, val in enumerate(machine_utilization[machine_name]) if val is not None]
        valid_hours = [hours[i] for i in valid_indices]
        valid_utilization = [machine_utilization[machine_name][i] for i in valid_indices]
        
        if valid_utilization:
            fig.add_trace(go.Scatter(
                x=valid_hours,
                y=valid_utilization,
                mode='lines+markers',
                name=machine_name
            ))
    
    # Add reference line at 70%
    if hours:
        fig.add_shape(
            type="line",
            x0=hours[0],
            y0=70,
            x1=hours[-1],
            y1=70,
            line=dict(
                color="red",
                width=2,
                dash="dash",
            )
        )
        
        # Annotate the threshold line
        fig.add_annotation(
            x=hours[-1],
            y=70,
            text="70% Threshold",
            showarrow=False,
            yshift=10,
            xshift=5
        )
    
    # Update layout
    fig.update_layout(
        title="Hourly Machine Utilization",
        xaxis_title="Hour",
        yaxis_title="Utilization (%)",
        yaxis=dict(range=[0, 100]),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def plot_inventory_impact(daily_data):
    """
    Create a visualization showing the impact of inventory status on machine utilization.
    
    Args:
        daily_data (list): List of hourly data entries for a day
        
    Returns:
        plotly.graph_objects.Figure: The plotly figure object
    """
    # Prepare data for plotting
    inventory_types = ["Wrapped", "Labelled", "Wrapped and Labelled", "Unlabelled", "Other"]
    inventory_data = {inv_type: [] for inv_type in inventory_types}
    
    # Collect utilization percentages for each inventory type
    for data in daily_data:
        for machine_name, machine_data in data['machines'].items():
            inventory_type = machine_data['inventory']
            utilization = machine_data['utilization']
            
            inventory_data[inventory_type].append(utilization)
    
    # Calculate statistics for each inventory type
    inventory_stats = {}
    for inv_type, utilization_list in inventory_data.items():
        if utilization_list:
            inventory_stats[inv_type] = {
                'mean': np.mean(utilization_list),
                'median': np.median(utilization_list),
                'count': len(utilization_list)
            }
        else:
            inventory_stats[inv_type] = {
                'mean': 0,
                'median': 0,
                'count': 0
            }
    
    # Convert to DataFrame for plotting
    df_stats = pd.DataFrame.from_dict(inventory_stats, orient='index')
    df_stats = df_stats.reset_index().rename(columns={'index': 'Inventory Type'})
    
    # Create box plot
    fig = go.Figure()
    
    for inv_type in inventory_types:
        data = inventory_data[inv_type]
        if data:
            fig.add_trace(go.Box(
                y=data,
                name=inv_type,
                boxmean=True  # adds mean as dashed line
            ))
    
    # Update layout
    fig.update_layout(
        title="Impact of Inventory Status on Machine Utilization",
        yaxis_title="Utilization (%)",
        yaxis=dict(range=[0, 100]),
        showlegend=False
    )
    
    # Add annotation for key findings
    impact_text = "Inventory Impact Analysis:\n"
    for inv_type in inventory_types:
        if inventory_stats[inv_type]['count'] > 0:
            impact_text += f"• {inv_type}: {inventory_stats[inv_type]['mean']:.1f}% avg. util. (n={inventory_stats[inv_type]['count']})\n"
    
    fig.add_annotation(
        x=0.01,
        y=0.99,
        xref="paper",
        yref="paper",
        text=impact_text,
        showarrow=False,
        align="left",
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="rgba(0,0,0,0.2)",
        borderwidth=1,
        borderpad=4
    )
    
    return fig
