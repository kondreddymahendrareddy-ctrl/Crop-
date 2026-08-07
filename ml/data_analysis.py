import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

def load_data(filepath="data/Crop_recommendation.csv"):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset not found at {filepath}")
    return pd.read_csv(filepath)

def plot_crop_distribution(df):
    """Plots the distribution of crops in the dataset."""
    crop_counts = df['label'].value_counts().reset_index()
    crop_counts.columns = ['Crop', 'Count']
    fig = px.bar(crop_counts, x='Crop', y='Count', title='Crop Distribution in Dataset',
                 color='Count', color_continuous_scale='Viridis')
    fig.update_layout(xaxis_tickangle=-45)
    return fig

def plot_feature_distribution(df, feature, color_scale='Blues'):
    """Plots a histogram for a specific numerical feature."""
    fig = px.histogram(df, x=feature, title=f'Distribution of {feature.capitalize()}',
                       color_discrete_sequence=[px.colors.sequential.Viridis[4]])
    return fig

def plot_correlation_heatmap(df):
    """Plots a correlation heatmap for numerical features."""
    numerical_df = df.select_dtypes(include=['int64', 'float64'])
    corr = numerical_df.corr()
    fig = px.imshow(corr, text_auto=True, aspect="auto", 
                    title="Correlation Heatmap of Numerical Features",
                    color_continuous_scale='RdBu_r')
    return fig

def plot_crop_wise_feature(df, feature):
    """Plots a boxplot for a feature across different crops."""
    fig = px.box(df, x='label', y=feature, title=f'{feature.capitalize()} required by different crops',
                 color='label')
    fig.update_layout(xaxis_tickangle=-45, showlegend=False)
    return fig

def get_dataset_summary(df):
    """Returns a summary of the dataset for the dashboard."""
    return {
        "Total Records": len(df),
        "Total Features": len(df.columns) - 1,
        "Total Crops": df['label'].nunique(),
        "Missing Values": df.isnull().sum().sum()
    }

if __name__ == "__main__":
    # Test the functions
    try:
        print("Loading data...")
        df = load_data()
        print("Data loaded successfully. Shape:", df.shape)
        
        print("Generating Crop Distribution Plot...")
        fig1 = plot_crop_distribution(df)
        
        print("Generating Feature Distribution Plot...")
        fig2 = plot_feature_distribution(df, 'N')
        
        print("Generating Correlation Heatmap...")
        fig3 = plot_correlation_heatmap(df)
        
        print("Generating Crop-wise Feature Plot...")
        fig4 = plot_crop_wise_feature(df, 'temperature')
        
        print("EDA generation complete. All functions work.")
    except Exception as e:
        print(f"Error during EDA test: {e}")
