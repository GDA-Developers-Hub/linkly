import React, { useState } from 'react';
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
import { Switch } from '@/components/ui/switch';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { UserPlus, Trash2 } from 'lucide-react';

interface User {
    id: number;
    username: string;
    email: string;
    is_active: boolean;
    is_google_ads_manager: boolean;
    last_login?: string;
}

interface UserManagementProps {
    users: User[];
    loading?: boolean;
    onAddUser: (email: string) => Promise<void>;
    onToggleRole: (userId: number, isManager: boolean) => Promise<void>;
    onRemoveUser: (userId: number) => Promise<void>;
}

export const UserManagement: React.FC<UserManagementProps> = ({
    users,
    loading = false,
    onAddUser,
    onToggleRole,
    onRemoveUser,
}) => {
    const [newUserEmail, setNewUserEmail] = useState('');
    const [isDialogOpen, setIsDialogOpen] = useState(false);

    const handleAddUser = async () => {
        if (newUserEmail) {
            await onAddUser(newUserEmail);
            setNewUserEmail('');
            setIsDialogOpen(false);
        }
    };

    return (
        <div className="space-y-4">
            <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold">User Management</h2>
                <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                    <DialogTrigger asChild>
                        <Button>
                            <UserPlus className="h-4 w-4 mr-2" />
                            Add User
                        </Button>
                    </DialogTrigger>
                    <DialogContent>
                        <DialogHeader>
                            <DialogTitle>Add New User</DialogTitle>
                            <DialogDescription>
                                Enter the email address of the user you want to add as a Google Ads manager.
                            </DialogDescription>
                        </DialogHeader>
                        <div className="py-4">
                            <Label htmlFor="email">Email Address</Label>
                            <Input
                                id="email"
                                type="email"
                                value={newUserEmail}
                                onChange={(e) => setNewUserEmail(e.target.value)}
                                placeholder="user@example.com"
                            />
                        </div>
                        <DialogFooter>
                            <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                                Cancel
                            </Button>
                            <Button onClick={handleAddUser}>Add User</Button>
                        </DialogFooter>
                    </DialogContent>
                </Dialog>
            </div>

            <div className="rounded-md border">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Username</TableHead>
                            <TableHead>Email</TableHead>
                            <TableHead>Status</TableHead>
                            <TableHead>Google Ads Manager</TableHead>
                            <TableHead>Last Login</TableHead>
                            <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {users.map((user) => (
                            <TableRow key={user.id} className={loading ? 'opacity-50' : ''}>
                                <TableCell className="font-medium">{user.username}</TableCell>
                                <TableCell>{user.email}</TableCell>
                                <TableCell>
                                    <Badge
                                        className={user.is_active ? 'bg-green-500' : 'bg-red-500'}
                                    >
                                        {user.is_active ? 'Active' : 'Inactive'}
                                    </Badge>
                                </TableCell>
                                <TableCell>
                                    <Switch
                                        checked={user.is_google_ads_manager}
                                        onCheckedChange={(checked) => onToggleRole(user.id, checked)}
                                    />
                                </TableCell>
                                <TableCell>
                                    {user.last_login
                                        ? new Date(user.last_login).toLocaleDateString()
                                        : 'Never'}
                                </TableCell>
                                <TableCell className="text-right">
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        onClick={() => onRemoveUser(user.id)}
                                    >
                                        <Trash2 className="h-4 w-4 text-red-500" />
                                    </Button>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </div>
        </div>
    );
}; 