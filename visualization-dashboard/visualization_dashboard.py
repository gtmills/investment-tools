#!/usr/bin/env python3
"""
Visualization Dashboard
Creates charts and graphs for investment analysis data
"""

import pandas as pd
import sys
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import Counter


def load_master_rankings() -> pd.DataFrame:
    """
    Load the master investment rankings
    
    Returns:
        DataFrame with master rankings
    """
    try:
        df = pd.read_excel('../master_investment_rankings.xlsx', sheet_name='All Rankings')
        print(f"[SUCCESS] Loaded {len(df)} stocks from master rankings")
        return df
    except FileNotFoundError:
        print("[ERROR] Master rankings file not found. Run master_aggregator.py first.")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to load master rankings: {e}")
        sys.exit(1)


def create_grade_distribution_chart(df: pd.DataFrame, output_dir: Path) -> None:
    """
    Create a bar chart showing investment grade distribution
    
    Args:
        df: Master rankings DataFrame
        output_dir: Output directory for charts
    """
    grade_counts = df['Investment_Grade'].value_counts().sort_index()
    
    # Define colors for grades
    colors = {
        'A+': '#006400',  # Dark green
        'A': '#228B22',   # Forest green
        'B+': '#90EE90',  # Light green
        'B': '#FFD700',   # Gold
        'C': '#FFA500',   # Orange
        'D': '#FF6347',   # Tomato
        'F': '#DC143C'    # Crimson
    }
    
    grade_colors = [colors.get(grade, '#808080') for grade in grade_counts.index]
    
    plt.figure(figsize=(12, 6))
    bars = plt.bar(grade_counts.index, grade_counts.values, color=grade_colors, edgecolor='black', linewidth=1.5)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.title('Investment Grade Distribution', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Investment Grade', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Stocks', fontsize=12, fontweight='bold')
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    
    filename = output_dir / 'grade_distribution.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[SUCCESS] Created grade distribution chart: {filename}")


def create_top_stocks_chart(df: pd.DataFrame, output_dir: Path, top_n: int = 20) -> None:
    """
    Create a horizontal bar chart of top N stocks
    
    Args:
        df: Master rankings DataFrame
        output_dir: Output directory for charts
        top_n: Number of top stocks to display
    """
    top_stocks = df.nsmallest(top_n, 'Composite_Score')
    
    # Create labels with ticker and company name
    labels = [f"{row['Ticker']} - {row['Company'][:30]}" for _, row in top_stocks.iterrows()]
    scores = top_stocks['Composite_Score'].values
    
    # Color by grade
    grade_colors = {
        'A+': '#006400',
        'A': '#228B22',
        'B+': '#90EE90',
        'B': '#FFD700',
        'C': '#FFA500'
    }
    colors = [grade_colors.get(grade, '#808080') for grade in top_stocks['Investment_Grade']]
    
    plt.figure(figsize=(12, 10))
    bars = plt.barh(range(len(labels)), scores, color=colors, edgecolor='black', linewidth=1)
    
    plt.yticks(range(len(labels)), labels, fontsize=9)
    plt.xlabel('Composite Score (Lower is Better)', fontsize=12, fontweight='bold')
    plt.title(f'Top {top_n} Investment Opportunities', fontsize=16, fontweight='bold', pad=20)
    plt.gca().invert_yaxis()  # Best stocks at top
    plt.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Add legend
    legend_elements = [mpatches.Patch(color=color, label=grade) 
                      for grade, color in grade_colors.items() if grade in top_stocks['Investment_Grade'].values]
    plt.legend(handles=legend_elements, loc='lower right', title='Grade')
    
    plt.tight_layout()
    
    filename = output_dir / f'top_{top_n}_stocks.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[SUCCESS] Created top {top_n} stocks chart: {filename}")


def create_sector_breakdown_chart(df: pd.DataFrame, output_dir: Path, top_n: int = 50) -> None:
    """
    Create a pie chart showing sector breakdown of top N stocks
    
    Args:
        df: Master rankings DataFrame
        output_dir: Output directory for charts
        top_n: Number of top stocks to analyze
    """
    top_stocks = df.nsmallest(top_n, 'Composite_Score')
    sector_counts = top_stocks['Sector'].value_counts()
    
    # Create pie chart
    plt.figure(figsize=(12, 8))
    colors = plt.cm.Set3(range(len(sector_counts)))
    
    wedges, texts, autotexts = plt.pie(
        sector_counts.values,
        labels=sector_counts.index,
        autopct='%1.1f%%',
        colors=colors,
        startangle=90,
        textprops={'fontsize': 10}
    )
    
    # Make percentage text bold
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(9)
    
    plt.title(f'Sector Distribution - Top {top_n} Stocks', fontsize=16, fontweight='bold', pad=20)
    plt.axis('equal')
    plt.tight_layout()
    
    filename = output_dir / f'sector_breakdown_top_{top_n}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[SUCCESS] Created sector breakdown chart: {filename}")


def create_tool_coverage_heatmap(df: pd.DataFrame, output_dir: Path, top_n: int = 30) -> None:
    """
    Create a heatmap showing which tools ranked which stocks
    
    Args:
        df: Master rankings DataFrame
        output_dir: Output directory for charts
        top_n: Number of top stocks to display
    """
    top_stocks = df.nsmallest(top_n, 'Composite_Score')
    
    # Tool columns
    tool_cols = ['Value_Ranker', 'Magic_Formula', 'FCF_Analyzer', 'Financial_Health',
                 'Graham_Calculator', 'Dividend_Aristocrats', 'Historical_Valuation', 'Earnings_Quality']
    
    # Create binary matrix (1 if tool ranked the stock, 0 if not)
    coverage_matrix = []
    stock_labels = []
    
    for _, row in top_stocks.iterrows():
        stock_labels.append(f"{row['Ticker']}")
        coverage = [1 if pd.notna(row[col]) else 0 for col in tool_cols]
        coverage_matrix.append(coverage)
    
    # Create heatmap
    fig, ax = plt.subplots(figsize=(12, 14))
    
    # Display the matrix
    im = ax.imshow(coverage_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
    
    # Set ticks and labels
    ax.set_xticks(range(len(tool_cols)))
    ax.set_yticks(range(len(stock_labels)))
    ax.set_xticklabels([col.replace('_', ' ') for col in tool_cols], rotation=45, ha='right', fontsize=9)
    ax.set_yticklabels(stock_labels, fontsize=9)
    
    # Add grid
    ax.set_xticks([x - 0.5 for x in range(1, len(tool_cols))], minor=True)
    ax.set_yticks([y - 0.5 for y in range(1, len(stock_labels))], minor=True)
    ax.grid(which='minor', color='gray', linestyle='-', linewidth=0.5)
    
    # Add title
    plt.title(f'Tool Coverage Heatmap - Top {top_n} Stocks', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Analysis Tools', fontsize=12, fontweight='bold')
    plt.ylabel('Stock Ticker', fontsize=12, fontweight='bold')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_ticks([0, 1])
    cbar.set_ticklabels(['Not Ranked', 'Ranked'])
    
    plt.tight_layout()
    
    filename = output_dir / f'tool_coverage_heatmap_top_{top_n}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[SUCCESS] Created tool coverage heatmap: {filename}")


def create_score_distribution_chart(df: pd.DataFrame, output_dir: Path) -> None:
    """
    Create a histogram showing composite score distribution
    
    Args:
        df: Master rankings DataFrame
        output_dir: Output directory for charts
    """
    plt.figure(figsize=(12, 6))
    
    # Create histogram
    n, bins, patches = plt.hist(df['Composite_Score'], bins=50, edgecolor='black', linewidth=0.5)
    
    # Color bins by grade ranges
    grade_ranges = {
        'A+': (0, 50),
        'A': (50, 100),
        'B+': (100, 150),
        'B': (150, 200),
        'C': (200, 300),
        'D/F': (300, 500)
    }
    
    colors = {
        'A+': '#006400',
        'A': '#228B22',
        'B+': '#90EE90',
        'B': '#FFD700',
        'C': '#FFA500',
        'D/F': '#FF6347'
    }
    
    for patch, left_edge in zip(patches, bins[:-1]):
        for grade, (low, high) in grade_ranges.items():
            if low <= left_edge < high:
                patch.set_facecolor(colors[grade])
                break
    
    plt.title('Composite Score Distribution', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Composite Score', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Stocks', fontsize=12, fontweight='bold')
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add legend
    legend_elements = [mpatches.Patch(color=color, label=f'{grade} ({low}-{high})') 
                      for grade, (low, high) in grade_ranges.items()]
    plt.legend(handles=legend_elements, loc='upper right', title='Grade Ranges')
    
    plt.tight_layout()
    
    filename = output_dir / 'score_distribution.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[SUCCESS] Created score distribution chart: {filename}")


def create_summary_dashboard(df: pd.DataFrame, output_dir: Path) -> None:
    """
    Create a summary dashboard with key statistics
    
    Args:
        df: Master rankings DataFrame
        output_dir: Output directory for charts
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Investment Analysis Dashboard', fontsize=20, fontweight='bold', y=0.995)
    
    # 1. Grade Distribution (top left)
    grade_counts = df['Investment_Grade'].value_counts().sort_index()
    colors_map = {'A+': '#006400', 'A': '#228B22', 'B+': '#90EE90', 'B': '#FFD700', 
                  'C': '#FFA500', 'D': '#FF6347', 'F': '#DC143C'}
    grade_colors = [colors_map.get(grade, '#808080') for grade in grade_counts.index]
    
    ax1.bar(grade_counts.index, grade_counts.values, color=grade_colors, edgecolor='black', linewidth=1.5)
    ax1.set_title('Grade Distribution', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Grade', fontsize=11)
    ax1.set_ylabel('Count', fontsize=11)
    ax1.grid(axis='y', alpha=0.3)
    
    # 2. Top 10 Sectors (top right)
    sector_counts = df['Sector'].value_counts().head(10)
    ax2.barh(range(len(sector_counts)), sector_counts.values, color='steelblue', edgecolor='black')
    ax2.set_yticks(range(len(sector_counts)))
    ax2.set_yticklabels(sector_counts.index, fontsize=9)
    ax2.set_title('Top 10 Sectors by Stock Count', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Number of Stocks', fontsize=11)
    ax2.invert_yaxis()
    ax2.grid(axis='x', alpha=0.3)
    
    # 3. Tool Coverage Distribution (bottom left)
    coverage_counts = df['Tools_Count'].value_counts().sort_index()
    ax3.bar(coverage_counts.index, coverage_counts.values, color='coral', edgecolor='black', linewidth=1.5)
    ax3.set_title('Tool Coverage Distribution', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Number of Tools', fontsize=11)
    ax3.set_ylabel('Number of Stocks', fontsize=11)
    ax3.grid(axis='y', alpha=0.3)
    
    # 4. Key Statistics (bottom right)
    ax4.axis('off')
    
    stats_text = f"""
    KEY STATISTICS
    
    Total Stocks Analyzed: {len(df)}
    
    Grade A+ Stocks: {len(df[df['Investment_Grade'] == 'A+'])}
    Grade A Stocks: {len(df[df['Investment_Grade'] == 'A'])}
    Grade B+ Stocks: {len(df[df['Investment_Grade'] == 'B+'])}
    
    Average Composite Score: {df['Composite_Score'].mean():.1f}
    Median Composite Score: {df['Composite_Score'].median():.1f}
    
    Average Tool Coverage: {df['Tools_Count'].mean():.1f}
    Max Tool Coverage: {int(df['Tools_Count'].max())}
    
    Total Sectors: {df['Sector'].nunique()}
    Most Common Sector: {df['Sector'].mode()[0]}
    
    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
    """
    
    ax4.text(0.1, 0.5, stats_text, fontsize=11, verticalalignment='center',
             family='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.tight_layout()
    
    filename = output_dir / 'summary_dashboard.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[SUCCESS] Created summary dashboard: {filename}")


def main():
    """Main execution function"""
    print("="*140)
    print("VISUALIZATION DASHBOARD")
    print("="*140)
    print("\nGenerating charts and graphs for investment analysis\n")
    
    # Load data
    df = load_master_rankings()
    
    # Create output directory
    output_dir = Path('visualizations')
    output_dir.mkdir(exist_ok=True)
    
    print(f"\nGenerating visualizations...\n")
    
    # Generate all charts
    create_grade_distribution_chart(df, output_dir)
    create_top_stocks_chart(df, output_dir, top_n=20)
    create_sector_breakdown_chart(df, output_dir, top_n=50)
    create_tool_coverage_heatmap(df, output_dir, top_n=30)
    create_score_distribution_chart(df, output_dir)
    create_summary_dashboard(df, output_dir)
    
    print("\n" + "="*140)
    print("VISUALIZATION COMPLETE")
    print("="*140)
    print(f"\nGenerated 6 visualizations in: {output_dir.absolute()}")
    print("\nFiles created:")
    print("  1. grade_distribution.png - Investment grade breakdown")
    print("  2. top_20_stocks.png - Top 20 investment opportunities")
    print("  3. sector_breakdown_top_50.png - Sector distribution of top 50")
    print("  4. tool_coverage_heatmap_top_30.png - Tool coverage for top 30 stocks")
    print("  5. score_distribution.png - Composite score histogram")
    print("  6. summary_dashboard.png - Comprehensive overview dashboard")
    print("\n" + "="*140)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExecution cancelled by user.")
        sys.exit(1)
