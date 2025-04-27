import { NextResponse } from "next/server"
import { getSocialBuAPI } from "@/lib/api"

export async function GET(request: Request) {
  try {
    // In a real app, you would get the user ID from the session
    const userId = "user_123"

    // Get API token from user record (simplified)
    const apiToken = "your_socialbu_api_token"

    // Initialize API client
    const api = getSocialBuAPI(apiToken)
    if (!api) {
      return NextResponse.json({ error: "API client not initialized" }, { status: 500 })
    }

    // Call SocialBu API
    const accounts = await api.getAccounts()

    return NextResponse.json(accounts)
  } catch (error) {
    console.error("Error fetching accounts:", error)
    return NextResponse.json({ error: "Failed to fetch accounts" }, { status: 500 })
  }
}
