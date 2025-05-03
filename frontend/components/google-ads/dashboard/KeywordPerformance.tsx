import React from 'react';
import { KeywordMetrics } from '@/types/google-ads';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';

interface KeywordPerformanceProps {
    keywords: KeywordMetrics[];
    loading?: boolean;
}

export const KeywordPerformance: React.FC<KeywordPerformanceProps> = ({
    keywords,
    loading = false,
}) => {
    const getMatchTypeColor = (matchType: string) => {
        switch (matchType) {
            case 'EXACT':
                return 'bg-blue-500';
            case 'PHRASE':
                return 'bg-purple-500';
            case 'BROAD':
                return 'bg-orange-500';
            default:
                return 'bg-gray-500';
        }
    };

    // Sort keywords by impressions in descending order
    const sortedKeywords = [...keywords].sort((a, b) => b.impressions - a.impressions);

    return (
        <div className="rounded-md border">
            <Table>
                <TableHeader>
                    <TableRow>
                        <TableHead>Keyword</TableHead>
                        <TableHead>Match Type</TableHead>
                        <TableHead>Impressions</TableHead>
                        <TableHead>Clicks</TableHead>
                        <TableHead>CTR</TableHead>
                        <TableHead>Cost</TableHead>
                        <TableHead>CPC</TableHead>
                        <TableHead>Conversions</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {sortedKeywords.map((keyword) => (
                        <TableRow key={`${keyword.keyword}-${keyword.match_type}-${keyword.date}`}>
                            <TableCell className="font-medium">{keyword.keyword}</TableCell>
                            <TableCell>
                                <Badge className={getMatchTypeColor(keyword.match_type)}>
                                    {keyword.match_type}
                                </Badge>
                            </TableCell>
                            <TableCell>{keyword.impressions.toLocaleString()}</TableCell>
                            <TableCell>{keyword.clicks.toLocaleString()}</TableCell>
                            <TableCell>{keyword.ctr.toFixed(2)}%</TableCell>
                            <TableCell>${keyword.cost.toFixed(2)}</TableCell>
                            <TableCell>${keyword.cpc.toFixed(2)}</TableCell>
                            <TableCell>{keyword.conversions.toLocaleString()}</TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </div>
    );
}; 