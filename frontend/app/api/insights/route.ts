import { NextResponse } from "next/server"
import { getSocialBuAPI } from "@/lib/api"

export async function GET(request: Request) {
  try {
    // In a real app, you would get the user ID from the session
    const userId = "user_123"

    // Get API token from user record (simplified)
    const apiToken = "your_socialbu_api_token"

    // Get query parameters
    const { searchParams } = new URL(request.url)
    const accountId = searchParams.get("account_id")
    const dateFrom = searchParams.get("date_from")
    const dateTo = searchParams.get("date_to")

    // Validate required parameters
    if (!accountId || !dateFrom || !dateTo) {
      return NextResponse.json(
        { error: "Missing required parameters: account_id, date_from, date_to" },
        { status: 400 },
      )
    }

    // Initialize API client
    const api = getSocialBuAPI(apiToken)
    if (!api) {
      return NextResponse.json({ error: "API client not initialized" }, { status: 500 })
    }

    // Call SocialBu API
    const insights = await api.getInsights({
      account_id: Number.parseInt(accountId),
      date_from: dateFrom,
      date_to: dateTo,
    })

    return NextResponse.json(insights)
  } catch (error) {
    console.error("Error fetching insights:", error)
    return NextResponse.json({ error: "Failed to fetch insights" }, { status: 500 })
  }
}
