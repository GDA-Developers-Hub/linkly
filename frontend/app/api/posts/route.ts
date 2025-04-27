import { NextResponse } from "next/server"
import { getSocialBuAPI } from "@/lib/api"

// Rate limiting middleware (simplified version)
const rateLimiter = async (userId: string) => {
  // In a real app, this would check a database for the user's rate limit
  // and track their API usage
  return {
    allowed: true,
    remaining: 1000,
    limit: 5000,
  }
}

export async function GET(request: Request) {
  try {
    // In a real app, you would get the user ID from the session
    const userId = "user_123"

    // Check rate limit
    const rateLimit = await rateLimiter(userId)
    if (!rateLimit.allowed) {
      return NextResponse.json(
        {
          error: "Rate limit exceeded",
          limit: rateLimit.limit,
          remaining: rateLimit.remaining,
        },
        { status: 429 },
      )
    }

    // Get API token from user record (simplified)
    const apiToken = "your_socialbu_api_token"

    // Get query parameters
    const { searchParams } = new URL(request.url)
    const status = searchParams.get("status") || undefined
    const accountId = searchParams.get("account_id")
      ? Number.parseInt(searchParams.get("account_id") as string)
      : undefined

    // Initialize API client
    const api = getSocialBuAPI(apiToken)
    if (!api) {
      return NextResponse.json({ error: "API client not initialized" }, { status: 500 })
    }

    // Call SocialBu API
    const posts = await api.getPosts({
      status: status as string | undefined,
      account_id: accountId,
    })

    return NextResponse.json(posts)
  } catch (error) {
    console.error("Error fetching posts:", error)
    return NextResponse.json({ error: "Failed to fetch posts" }, { status: 500 })
  }
}

export async function POST(request: Request) {
  try {
    // In a real app, you would get the user ID from the session
    const userId = "user_123"

    // Check rate limit
    const rateLimit = await rateLimiter(userId)
    if (!rateLimit.allowed) {
      return NextResponse.json(
        {
          error: "Rate limit exceeded",
          limit: rateLimit.limit,
          remaining: rateLimit.remaining,
        },
        { status: 429 },
      )
    }

    // Get API token from user record (simplified)
    const apiToken = "your_socialbu_api_token"

    // Get request body
    const data = await request.json()
    const { content, account_ids, media_ids, scheduled_at } = data

    // Validate required fields
    if (!content || !account_ids || !Array.isArray(account_ids)) {
      return NextResponse.json({ error: "Missing required fields" }, { status: 400 })
    }

    // Initialize API client
    const api = getSocialBuAPI(apiToken)
    if (!api) {
      return NextResponse.json({ error: "API client not initialized" }, { status: 500 })
    }

    // Call SocialBu API
    const post = await api.createPost({
      content,
      account_ids,
      media_ids,
      scheduled_at,
    })

    return NextResponse.json(post)
  } catch (error) {
    console.error("Error creating post:", error)
    return NextResponse.json({ error: "Failed to create post" }, { status: 500 })
  }
}
