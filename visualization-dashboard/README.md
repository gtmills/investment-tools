# Visualization Dashboard

Creates professional charts and graphs to visualize investment analysis data.

## Overview

The Visualization Dashboard transforms the master rankings data into easy-to-understand visual representations, including:
- **Grade Distribution**: Bar chart showing investment grade breakdown
- **Top Stocks**: Horizontal bar chart of top 20 opportunities
- **Sector Breakdown**: Pie chart of sector allocation in top 50
- **Tool Coverage Heatmap**: Visual representation of which tools ranked which stocks
- **Score Distribution**: Histogram showing composite score ranges
- **Summary Dashboard**: Comprehensive 4-panel overview

## Features

- **High-Quality Charts**: 300 DPI PNG images suitable for presentations
- **Color-Coded Grades**: Consistent color scheme across all visualizations
- **Automated Generation**: Creates all charts with one command
- **Professional Styling**: Clean, publication-ready graphics
- **Comprehensive Coverage**: Multiple perspectives on the data

## Requirements

Install matplotlib if not already installed:

```bash
pip install matplotlib>=3.7.0
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

## Usage

```bash
cd visualization-dashboard
python visualization_dashboard.py
```

This generates 6 visualization files in the `visualizations/` directory.

## Output Files

All charts are saved as high-resolution PNG files (300 DPI):

### 1. grade_distribution.png
Bar chart showing the number of stocks in each investment grade (A+ through F).

**Use case**: Quickly see the overall quality distribution of analyzed stocks.

### 2. top_20_stocks.png
Horizontal bar chart displaying the top 20 investment opportunities with their composite scores, color-coded by grade.

**Use case**: Identify the best opportunities at a glance.

### 3. sector_breakdown_top_50.png
Pie chart showing sector allocation among the top 50 ranked stocks.

**Use case**: Understand sector concentration in elite opportunities.

### 4. tool_coverage_heatmap_top_30.png
Heatmap showing which of the 8 analysis tools ranked each of the top 30 stocks.

**Use case**: Assess conviction level - stocks ranked by more tools have higher confidence.

### 5. score_distribution.png
Histogram showing the distribution of composite scores across all stocks, color-coded by grade ranges.

**Use case**: Understand the overall score distribution and grade thresholds.

### 6. summary_dashboard.png
Comprehensive 4-panel dashboard with:
- Grade distribution
- Top 10 sectors by stock count
- Tool coverage distribution
- Key statistics summary

**Use case**: Single-page overview for presentations or reports.

## Color Scheme

Consistent color coding across all visualizations:

- **A+ Grade**: Dark Green (#006400)
- **A Grade**: Forest Green (#228B22)
- **B+ Grade**: Light Green (#90EE90)
- **B Grade**: Gold (#FFD700)
- **C Grade**: Orange (#FFA500)
- **D Grade**: Tomato (#FF6347)
- **F Grade**: Crimson (#DC143C)

## Integration with Other Tools

The Visualization Dashboard works with:
- **Master Aggregator**: Source of ranking data
- **Portfolio Builder**: Visualize portfolio composition
- **Alert System**: Chart ranking changes over time

## Customization

You can modify the charts by editing the script:

```python
# Change number of top stocks displayed
create_top_stocks_chart(df, output_dir, top_n=30)  # Default: 20

# Change sector breakdown scope
create_sector_breakdown_chart(df, output_dir, top_n=100)  # Default: 50

# Change heatmap size
create_tool_coverage_heatmap(df, output_dir, top_n=50)  # Default: 30
```

## Example Visualizations

### Grade Distribution
Shows how many stocks fall into each investment grade category, helping you understand the overall quality of opportunities.

### Top 20 Stocks
Displays the best opportunities with their composite scores. Lower scores are better. Color coding helps identify grade levels quickly.

### Sector Breakdown
Reveals which sectors dominate the top opportunities. Useful for ensuring diversification or identifying sector trends.

### Tool Coverage Heatmap
Green cells indicate a tool ranked that stock. More green = higher conviction. Helps identify stocks with broad agreement across methodologies.

### Score Distribution
Shows the full range of composite scores. Most stocks cluster in the middle ranges, with elite opportunities having very low scores.

### Summary Dashboard
Four-panel overview providing:
- Grade counts
- Sector representation
- Tool coverage statistics
- Key metrics summary

## Best Practices

1. **Generate After Each Run**: Create fresh visualizations after running master aggregator
2. **Use in Presentations**: High-resolution images suitable for reports and presentations
3. **Compare Over Time**: Save dated copies to track changes
4. **Share with Team**: Visual format easier to communicate than spreadsheets
5. **Identify Patterns**: Look for sector concentrations or grade clusters
6. **Verify Quality**: Check tool coverage heatmap for conviction levels

## Technical Details

- **Image Format**: PNG (Portable Network Graphics)
- **Resolution**: 300 DPI (print quality)
- **Color Space**: RGB
- **Chart Library**: Matplotlib
- **Figure Sizes**: Optimized for readability (10-16 inches wide)

## Limitations

- Static images only (no interactive charts)
- Requires matplotlib installation
- Large datasets may make some charts crowded
- No animation or time-series visualizations
- Manual regeneration required for updates

## Future Enhancements

Potential improvements:
- Interactive HTML dashboards
- Time-series animations showing ranking changes
- Correlation matrices between tools
- Risk-return scatter plots
- Sector performance comparisons
- Custom color schemes
- PDF report generation
- Automated email delivery

## Troubleshooting

**"matplotlib not found"**
- Install with: `pip install matplotlib>=3.7.0`

**Charts look crowded**
- Reduce `top_n` parameter in function calls
- Increase figure size in the code

**Colors not displaying correctly**
- Ensure using RGB color space
- Check display color calibration

**Low resolution images**
- DPI is set to 300 by default
- Increase if needed: `plt.savefig(filename, dpi=600)`

## Notes

- All visualizations are regenerated each run
- Previous versions are overwritten
- Charts use data from master_investment_rankings.xlsx
- Output directory created automatically if it doesn't exist
- Suitable for both screen display and printing