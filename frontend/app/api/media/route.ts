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
    const media = await api.getMedia()

    return NextResponse.json(media)
  } catch (error) {
    console.error("Error fetching media:", error)
    return NextResponse.json({ error: "Failed to fetch media" }, { status: 500 })
  }
}

export async function POST(request: Request) {
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

    // Parse the multipart form data
    const formData = await request.formData()
    const file = formData.get("file") as File

    if (!file) {
      return NextResponse.json({ error: "No file provided" }, { status: 400 })
    }

    // Call SocialBu API
    const media = await api.uploadMedia(file)

    return NextResponse.json(media)
  } catch (error) {
    console.error("Error uploading media:", error)
    return NextResponse.json({ error: "Failed to upload media" }, { status: 500 })
  }
}
