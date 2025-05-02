import { Team } from "@/lib/socialbu-api"

const MOCK_TEAMS: Team[] = [
  { id: 1, name: "Marketing Team", created_at: new Date().toISOString() },
  { id: 2, name: "Content Creation", created_at: new Date().toISOString() },
]

export default function TeamsPage() {
  return (
    <div>
      <h1>Teams</h1>
      <div>
        {MOCK_TEAMS.map(team => (
          <div key={team.id}>
            <h2>{team.name}</h2>
            <p>Created: {new Date(team.created_at).toLocaleDateString()}</p>
          </div>
        ))}
      </div>
    </div>
  )
} 