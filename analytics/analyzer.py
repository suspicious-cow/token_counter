"""
Enhanced analytics and visualization for experiment results.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional
import numpy as np
from pathlib import Path


class ExperimentAnalyzer:
    """Analyzer for experiment results with visualization capabilities"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize analyzer with experiment data.
        
        Args:
            df: DataFrame with experiment results
        """
        self.df = df
        self.successful_df = df[~df['Output'].str.startswith('Error:', na=False)]
        
    def generate_cost_comparison_chart(self, output_dir: str = "outputs"):
        """Generate cost comparison visualization"""
        if self.successful_df.empty:
            print("No successful calls to analyze")
            return
            
        plt.figure(figsize=(12, 8))
        
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # Cost distribution by provider
        sns.boxplot(data=self.successful_df, x='Vendor', y='Cost (USD)', ax=ax1)
        ax1.set_title('Cost Distribution by Provider')
        ax1.tick_params(axis='x', rotation=45)
        
        # Token usage comparison
        token_data = self.successful_df.melt(
            id_vars=['Vendor'], 
            value_vars=['Input Tokens', 'Output Tokens'],
            var_name='Token Type', 
            value_name='Count'
        )
        sns.barplot(data=token_data, x='Vendor', y='Count', hue='Token Type', ax=ax2)
        ax2.set_title('Token Usage by Provider')
        ax2.tick_params(axis='x', rotation=45)
        
        # Cost per output token
        self.successful_df['Cost per Output Token'] = (
            self.successful_df['Cost (USD)'] / self.successful_df['Output Tokens']
        ).replace([np.inf, -np.inf], np.nan)
        
        sns.barplot(data=self.successful_df, x='Vendor', y='Cost per Output Token', ax=ax3)
        ax3.set_title('Cost Efficiency (Cost per Output Token)')
        ax3.tick_params(axis='x', rotation=45)
        
        # Success rate by provider
        success_rates = self.calculate_success_rates()
        providers = list(success_rates.keys())
        rates = list(success_rates.values())
        
        ax4.bar(providers, rates)
        ax4.set_title('Success Rate by Provider')
        ax4.set_ylabel('Success Rate (%)')
        ax4.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # Save chart
        output_path = Path(output_dir) / 'cost_comparison.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Cost comparison chart saved to {output_path}")
        plt.close()
    
    def generate_token_efficiency_report(self) -> pd.Series:
        """
        Analyze tokens per dollar efficiency.
        
        Returns:
            Series with efficiency metrics by provider
        """
        if self.successful_df.empty:
            return pd.Series()
            
        efficiency = self.successful_df.groupby('Vendor').apply(
            lambda x: x['Output Tokens'].sum() / x['Cost (USD)'].sum() 
            if x['Cost (USD)'].sum() > 0 else 0
        )
        
        return efficiency.sort_values(ascending=False)
    
    def calculate_success_rates(self) -> Dict[str, float]:
        """Calculate success rate by provider"""
        total_by_vendor = self.df['Vendor'].value_counts()
        successful_by_vendor = self.successful_df['Vendor'].value_counts()
        
        success_rates = {}
        for vendor in total_by_vendor.index:
            total = total_by_vendor[vendor]
            successful = successful_by_vendor.get(vendor, 0)
            success_rates[vendor] = (successful / total) * 100
            
        return success_rates
    
    def detect_outliers(self) -> Dict[str, List]:
        """
        Identify unusual responses or costs.
        
        Returns:
            Dict with outlier information
        """
        outliers = {
            'high_cost': [],
            'high_tokens': [],
            'unusual_responses': []
        }
        
        if self.successful_df.empty:
            return outliers
        
        # Cost outliers (beyond 2 standard deviations)
        cost_mean = self.successful_df['Cost (USD)'].mean()
        cost_std = self.successful_df['Cost (USD)'].std()
        cost_threshold = cost_mean + 2 * cost_std
        
        high_cost_mask = self.successful_df['Cost (USD)'] > cost_threshold
        outliers['high_cost'] = self.successful_df[high_cost_mask].to_dict('records')
        
        # Token outliers
        token_mean = self.successful_df['Output Tokens'].mean()
        token_std = self.successful_df['Output Tokens'].std()
        token_threshold = token_mean + 2 * token_std
        
        high_token_mask = self.successful_df['Output Tokens'] > token_threshold
        outliers['high_tokens'] = self.successful_df[high_token_mask].to_dict('records')
        
        # Unusual response lengths (very short or very long)
        self.successful_df['Response Length'] = self.successful_df['Output'].str.len()
        response_q1 = self.successful_df['Response Length'].quantile(0.25)
        response_q3 = self.successful_df['Response Length'].quantile(0.75)
        iqr = response_q3 - response_q1
        
        unusual_mask = (
            (self.successful_df['Response Length'] < response_q1 - 1.5 * iqr) |
            (self.successful_df['Response Length'] > response_q3 + 1.5 * iqr)
        )
        outliers['unusual_responses'] = self.successful_df[unusual_mask].to_dict('records')
        
        return outliers
    
    def generate_comprehensive_report(self, output_dir: str = "outputs") -> str:
        """
        Generate a comprehensive analysis report.
        
        Args:
            output_dir: Directory to save the report
            
        Returns:
            Path to the generated report
        """
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("COMPREHENSIVE EXPERIMENT ANALYSIS")
        report_lines.append("=" * 60)
        
        # Basic statistics
        total_calls = len(self.df)
        successful_calls = len(self.successful_df)
        failed_calls = total_calls - successful_calls
        
        report_lines.append(f"\nBasic Statistics:")
        report_lines.append(f"  Total API calls: {total_calls}")
        report_lines.append(f"  Successful calls: {successful_calls}")
        report_lines.append(f"  Failed calls: {failed_calls}")
        report_lines.append(f"  Overall success rate: {(successful_calls/total_calls)*100:.1f}%")
        
        # Success rates by provider
        success_rates = self.calculate_success_rates()
        report_lines.append(f"\nSuccess Rates by Provider:")
        for provider, rate in success_rates.items():
            report_lines.append(f"  {provider}: {rate:.1f}%")
        
        # Cost analysis
        if not self.successful_df.empty:
            report_lines.append(f"\nCost Analysis:")
            cost_stats = self.successful_df.groupby('Vendor')['Cost (USD)'].agg(['mean', 'sum', 'std'])
            for vendor in cost_stats.index:
                mean_cost = cost_stats.loc[vendor, 'mean']
                total_cost = cost_stats.loc[vendor, 'sum']
                std_cost = cost_stats.loc[vendor, 'std']
                report_lines.append(f"  {vendor}:")
                report_lines.append(f"    Average cost: ${mean_cost:.6f}")
                report_lines.append(f"    Total cost: ${total_cost:.6f}")
                report_lines.append(f"    Cost std dev: ${std_cost:.6f}")
            
            # Token efficiency
            efficiency = self.generate_token_efficiency_report()
            report_lines.append(f"\nToken Efficiency (Output Tokens per Dollar):")
            for vendor, eff in efficiency.items():
                report_lines.append(f"  {vendor}: {eff:,.0f} tokens/$")
        
        # Outlier detection
        outliers = self.detect_outliers()
        report_lines.append(f"\nOutlier Detection:")
        report_lines.append(f"  High cost outliers: {len(outliers['high_cost'])}")
        report_lines.append(f"  High token outliers: {len(outliers['high_tokens'])}")
        report_lines.append(f"  Unusual responses: {len(outliers['unusual_responses'])}")
        
        # Save report
        report_content = "\n".join(report_lines)
        output_path = Path(output_dir) / 'comprehensive_analysis.txt'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"Comprehensive analysis saved to {output_path}")
        return str(output_path)