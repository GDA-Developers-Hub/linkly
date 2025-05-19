"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { toast } from "@/components/ui/use-toast"
import type { Team, TeamMember } from "@/lib/socials-api"
import { MoreHorizontal, Plus, UserPlus, Mail, Shield, Crown, Users, UserX } from "lucide-react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

// Mock data for development
const MOCK_TEAMS: Team[] = [
  { id: 1, name: "Marketing Team", created_at: new Date().toISOString() },
  { id: 2, name: "Content Creation", created_at: new Date().toISOString() },
]

const MOCK_MEMBERS: TeamMember[] = [
  {
    id: 1,
    name: "John Doe",
    email: "john@example.com",
    role: "Admin",
    joined_at: new Date().toISOString(),
  },
  {
    id: 2,
    name: "Jane Smith",
    email: "jane@example.com",
    role: "Editor",
    joined_at: new Date().toISOString(),
  },
  {
    id: 3,
    name: "Mike Johnson",
    email: "mike@example.com",
    role: "Viewer",
    joined_at: new Date().toISOString(),
  },
]

const MOCK_INVITES = [
  { id: 1, email: "alex@example.com", role: "Editor", sent_at: "2023-04-15T10:30:00Z" },
  { id: 2, email: "taylor@example.com", role: "Viewer", sent_at: "2023-04-16T14:45:00Z" },
]

export default function TeamPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [teams, setTeams] = useState<Team[]>([])
  const [members, setMembers] = useState<TeamMember[]>([])
  const [invites, setInvites] = useState<any[]>([])
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null)
  const [newTeamName, setNewTeamName] = useState("")
  const [newMemberName, setNewMemberName] = useState("")
  const [newMemberEmail, setNewMemberEmail] = useState("")
  const [newMemberRole, setNewMemberRole] = useState("Editor")
  const [isAddingTeam, setIsAddingTeam] = useState(false)
  const [isInvitingMember, setIsInvitingMember] = useState(false)
  const [selectedPlatform, setSelectedPlatform] = useState("all")

  // Load data
  useEffect(() => {
    const loadData = async () => {
      try {
        setIsLoading(true)
        // In a real app, we would fetch from the API
        // const api = getSocialBuAPI()
        // const teamsData = await api.getTeams()
        // const membersData = await api.getTeamMembers(selectedTeam?.id || 1)

        // Using mock data for now
        setTeams(MOCK_TEAMS)
        setMembers(MOCK_MEMBERS)
        setInvites(MOCK_INVITES)
        setSelectedTeam(MOCK_TEAMS[0])
      } catch (error) {
        console.error("Failed to load team data", error)
        toast({
          title: "Error",
          description: "Failed to load team data. Please try again.",
          variant: "destructive",
        })
      } finally {
        setIsLoading(false)
      }
    }

    loadData()
  }, [])

  const handleCreateTeam = async () => {
    if (!newTeamName.trim()) {
      toast({
        title: "Error",
        description: "Team name cannot be empty",
        variant: "destructive",
      })
      return
    }

    try {
      // In a real app, we would call the API
      // const api = getSocialBuAPI()
      // const newTeam = await api.createTeam(newTeamName)

      // Using mock data for now
      const newTeam: Team = {
        id: Math.floor(Math.random() * 1000) + 10,
        name: newTeamName,
        created_at: new Date().toISOString(),
      }

      setTeams([...teams, newTeam])
      setNewTeamName("")
      setIsAddingTeam(false)

      toast({
        title: "Success",
        description: `Team "${newTeamName}" has been created`,
      })
    } catch (error) {
      console.error("Failed to create team", error)
      toast({
        title: "Error",
        description: "Failed to create team. Please try again.",
        variant: "destructive",
      })
    }
  }

  const handleAddMember = () => {
    const newMember: TeamMember = {
      id: Math.floor(Math.random() * 1000) + 10,
      name: newMemberName,
      email: newMemberEmail,
      role: newMemberRole,
      joined_at: new Date().toISOString(),
    }
    // In a real app, you would make an API call here
    setMembers([...members, newMember])
    setNewMemberName("")
    setNewMemberEmail("")
    setNewMemberRole("Viewer")
    setIsInvitingMember(false)
  }

  const handleInviteMember = async () => {
    if (!newMemberEmail.trim()) {
      toast({
        title: "Error",
        description: "Email cannot be empty",
        variant: "destructive",
      })
      return
    }

    try {
      // In a real app, we would call the API
      // const api = getSocialBuAPI()
      // await api.inviteTeamMember(selectedTeam?.id || 1, newMemberEmail, newMemberRole)

      // Using mock data for now
      const newInvite = {
        id: Math.floor(Math.random() * 1000) + 10,
        email: newMemberEmail,
        role: newMemberRole,
        sent_at: new Date().toISOString(),
      }

      setInvites([...invites, newInvite])
      setNewMemberEmail("")
      setIsInvitingMember(false)

      toast({
        title: "Success",
        description: `Invitation sent to ${newMemberEmail}`,
      })
    } catch (error) {
      console.error("Failed to invite member", error)
      toast({
        title: "Error",
        description: "Failed to send invitation. Please try again.",
        variant: "destructive",
      })
    }
  }

  const handleRemoveMember = async (memberId: number) => {
    try {
      // In a real app, you would make an API call here
      setMembers(members.filter((member) => member.id !== memberId))

      toast({
        title: "Member removed",
        description: "Team member has been removed successfully.",
      })
    } catch (error) {
      console.error("Failed to remove member:", error)
      toast({
        title: "Error",
        description: "Failed to remove team member. Please try again.",
        variant: "destructive",
      })
    }
  }

  const handleCancelInvite = async (inviteId: number) => {
    try {
      // In a real app, we would call the API
      // const api = getSocialBuAPI()
      // await api.cancelInvitation(inviteId)

      // Using mock data for now
      setInvites(invites.filter((invite) => invite.id !== inviteId))

      toast({
        title: "Success",
        description: "Invitation has been canceled",
      })
    } catch (error) {
      console.error("Failed to cancel invitation", error)
      toast({
        title: "Error",
        description: "Failed to cancel invitation. Please try again.",
        variant: "destructive",
      })
    }
  }

  const handleChangeRole = async (memberId: number, newRole: string) => {
    try {
      // In a real app, you would make an API call here
      setMembers(members.map((member) => (member.id === memberId ? { ...member, role: newRole } : member)))

      toast({
        title: "Role updated",
        description: "Team member's role has been updated successfully.",
      })
    } catch (error) {
      console.error("Failed to change role:", error)
      toast({
        title: "Error",
        description: "Failed to update team member's role. Please try again.",
        variant: "destructive",
      })
    }
  }

  const getRoleIcon = (role: string) => {
    switch (role) {
      case "Admin":
        return <Crown className="h-4 w-4 text-yellow-500" />
      case "Editor":
        return <Shield className="h-4 w-4 text-blue-500" />
      case "Viewer":
        return <Users className="h-4 w-4 text-gray-500" />
      default:
        return null
    }
  }

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((part) => part[0])
      .join("")
      .toUpperCase()
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-10 w-32" />
        </div>
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-32 mb-2" />
            <Skeleton className="h-4 w-64" />
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="flex items-center space-x-4">
                  <Skeleton className="h-10 w-10 rounded-full" />
                  <div className="space-y-2">
                    <Skeleton className="h-4 w-32" />
                    <Skeleton className="h-3 w-24" />
                  </div>
                  <div className="ml-auto">
                    <Skeleton className="h-8 w-8 rounded-full" />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Team Management</h1>
          <p className="text-muted-foreground">Manage your team members and their permissions</p>
        </div>
        <div className="flex items-center gap-2">
          <Dialog open={isAddingTeam} onOpenChange={setIsAddingTeam}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <Plus className="h-4 w-4 mr-2" />
                New Team
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New Team</DialogTitle>
                <DialogDescription>
                  Create a new team to organize your team members and their permissions.
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="team-name">Team Name</Label>
                  <Input
                    id="team-name"
                    placeholder="Marketing Team"
                    value={newTeamName}
                    onChange={(e) => setNewTeamName(e.target.value)}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsAddingTeam(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateTeam}>Create Team</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          <Dialog open={isInvitingMember} onOpenChange={setIsInvitingMember}>
            <DialogTrigger asChild>
              <Button>
                <UserPlus className="h-4 w-4 mr-2" />
                Invite Member
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Invite Team Member</DialogTitle>
                <DialogDescription>Invite a new member to join your team.</DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="email">Email Address</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="email@example.com"
                    value={newMemberEmail}
                    onChange={(e) => setNewMemberEmail(e.target.value)}
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="role">Role</Label>
                  <Select
                    value={newMemberRole}
                    onValueChange={setNewMemberRole}
                    aria-label="Select role"
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select role" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Admin">Admin</SelectItem>
                      <SelectItem value="Editor">Editor</SelectItem>
                      <SelectItem value="Viewer">Viewer</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsInvitingMember(false)}>
                  Cancel
                </Button>
                <Button onClick={handleInviteMember}>Send Invitation</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <div className="grid gap-6">
        {teams.length > 0 && (
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Teams</CardTitle>
                  <CardDescription>Select a team to manage its members</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue={selectedTeam?.id.toString() || "1"} className="w-full">
                <TabsList className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 mb-4">
                  {teams.map((team) => (
                    <TabsTrigger key={team.id} value={team.id.toString()} onClick={() => setSelectedTeam(team)}>
                      {team.name}
                    </TabsTrigger>
                  ))}
                </TabsList>
              </Tabs>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader>
            <CardTitle>Team Members</CardTitle>
            <CardDescription>Manage members in {selectedTeam?.name || "your team"}</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {members.map((member) => (
                  <TableRow key={member.id}>
                    <TableCell className="font-medium">
                      <div className="flex items-center gap-2">
                        <Avatar className="h-8 w-8">
                          <AvatarImage src={`https://avatar.vercel.sh/${member.id}`} alt={member.name} />
                          <AvatarFallback>{getInitials(member.name)}</AvatarFallback>
                        </Avatar>
                        {member.name}
                      </div>
                    </TableCell>
                    <TableCell>{member.email}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        {getRoleIcon(member.role)}
                        {member.role}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant={member.role === "Admin" ? "default" : "outline"}>
                        {member.role === "Admin" ? "Admin" : "Member"}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreHorizontal className="h-4 w-4" />
                            <span className="sr-only">Open menu</span>
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuLabel>Actions</DropdownMenuLabel>
                          <DropdownMenuItem onClick={() => (window.location.href = `mailto:${member.email}`)}>
                            <Mail className="h-4 w-4 mr-2" />
                            Email
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem onClick={() => handleChangeRole(member.id, "Admin")}>
                            <Crown className="h-4 w-4 mr-2" />
                            Make Admin
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => handleChangeRole(member.id, "Editor")}>
                            <Shield className="h-4 w-4 mr-2" />
                            Make Editor
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => handleChangeRole(member.id, "Viewer")}>
                            <Users className="h-4 w-4 mr-2" />
                            Make Viewer
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem className="text-red-600" onClick={() => handleRemoveMember(member.id)}>
                            <UserX className="h-4 w-4 mr-2" />
                            Remove
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {invites.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Pending Invitations</CardTitle>
              <CardDescription>Manage pending team invitations</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Email</TableHead>
                    <TableHead>Role</TableHead>
                    <TableHead>Sent</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {invites.map((invite) => (
                    <TableRow key={invite.id}>
                      <TableCell className="font-medium">{invite.email}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          {getRoleIcon(invite.role)}
                          {invite.role}
                        </div>
                      </TableCell>
                      <TableCell>{new Date(invite.sent_at).toLocaleDateString()}</TableCell>
                      <TableCell className="text-right">
                        <Button variant="ghost" size="sm" onClick={() => handleCancelInvite(invite.id)}>
                          Cancel
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            navigator.clipboard.writeText(`${window.location.origin}/invite/${invite.id}`)
                            toast({
                              title: "Copied",
                              description: "Invitation link copied to clipboard",
                            })
                          }}
                        >
                          Copy Link
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
