import React from 'react';
import { Campaign } from '@/types/google-ads';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { RefreshCw } from 'lucide-react';

interface CampaignsListProps {
    campaigns: Campaign[];
    loading?: boolean;
    onSync?: (id: string) => void;
    onSelect?: (campaign: Campaign) => void;
}

export const CampaignsList: React.FC<CampaignsListProps> = ({
    campaigns,
    loading = false,
    onSync,
    onSelect,
}) => {
    const getStatusColor = (status: string) => {
        switch (status) {
            case 'ENABLED':
                return 'bg-green-500';
            case 'PAUSED':
                return 'bg-yellow-500';
            case 'REMOVED':
                return 'bg-red-500';
            default:
                return 'bg-gray-500';
        }
    };

    return (
        <div className="rounded-md border">
            <Table>
                <TableHeader>
                    <TableRow>
                        <TableHead>Name</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Budget</TableHead>
                        <TableHead>Start Date</TableHead>
                        <TableHead>End Date</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {campaigns.map((campaign) => (
                        <TableRow
                            key={campaign.id}
                            className={`cursor-pointer ${loading ? 'opacity-50' : ''}`}
                            onClick={() => onSelect?.(campaign)}
                        >
                            <TableCell className="font-medium">{campaign.name}</TableCell>
                            <TableCell>
                                <Badge className={getStatusColor(campaign.status)}>
                                    {campaign.status}
                                </Badge>
                            </TableCell>
                            <TableCell>${campaign.budget.toFixed(2)}</TableCell>
                            <TableCell>{new Date(campaign.start_date).toLocaleDateString()}</TableCell>
                            <TableCell>
                                {campaign.end_date
                                    ? new Date(campaign.end_date).toLocaleDateString()
                                    : 'No end date'}
                            </TableCell>
                            <TableCell className="text-right">
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        onSync?.(campaign.id);
                                    }}
                                >
                                    <RefreshCw className="h-4 w-4" />
                                </Button>
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </div>
    );
}; 