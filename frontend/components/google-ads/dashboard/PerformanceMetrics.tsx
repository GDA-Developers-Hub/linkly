import React from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { PerformanceSummary } from '@/types/google-ads';

interface PerformanceMetricsProps {
    data: PerformanceSummary;
    loading?: boolean;
}

export const PerformanceMetrics: React.FC<PerformanceMetricsProps> = ({ data, loading = false }) => {
    const metrics = [
        {
            label: 'Impressions',
            value: data.total_impressions.toLocaleString(),
            description: 'Total number of times your ads were shown'
        },
        {
            label: 'Clicks',
            value: data.total_clicks.toLocaleString(),
            description: 'Total number of clicks on your ads'
        },
        {
            label: 'Cost',
            value: `$${data.total_cost.toLocaleString(undefined, { minimumFractionDigits: 2 })}`,
            description: 'Total spend on your campaigns'
        },
        {
            label: 'Conversions',
            value: data.total_conversions.toLocaleString(),
            description: 'Total number of conversions from your ads'
        },
        {
            label: 'CTR',
            value: `${((data.total_clicks / data.total_impressions) * 100).toFixed(2)}%`,
            description: 'Click-through rate'
        },
        {
            label: 'CPC',
            value: `$${(data.total_cost / data.total_clicks).toFixed(2)}`,
            description: 'Average cost per click'
        }
    ];

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {metrics.map((metric) => (
                <Card key={metric.label} className={loading ? 'opacity-50' : ''}>
                    <CardHeader className="pb-2">
                        <h3 className="text-sm font-medium text-muted-foreground">
                            {metric.label}
                        </h3>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{metric.value}</div>
                        <p className="text-sm text-muted-foreground mt-1">
                            {metric.description}
                        </p>
                    </CardContent>
                </Card>
            ))}
        </div>
    );
}; 