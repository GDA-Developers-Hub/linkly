import { NextResponse } from "next/server"

// This would be replaced with a real database in production
const users: any[] = []

// Subscription plans with rate limits
const subscriptionPlans = {
  free: {
    maxPosts: 50,
    maxStorage: 500, // MB
    maxApiCalls: 5000,
    price: 0,
  },
  pro: {
    maxPosts: 200,
    maxStorage: 2000, // MB
    maxApiCalls: 20000,
    price: 29,
  },
  business: {
    maxPosts: -1, // unlimited
    maxStorage: 10000, // MB
    maxApiCalls: 100000,
    price: 99,
  },
}

export async function POST(request: Request) {
  try {
    const data = await request.json()
    const { email, password, firstName, lastName, accountType, plan } = data

    // Check if user already exists
    if (users.some((user) => user.email === email)) {
      return NextResponse.json({ error: "User with this email already exists" }, { status: 400 })
    }

    // Get subscription plan details
    const subscription = subscriptionPlans[plan as keyof typeof subscriptionPlans] || subscriptionPlans.free

    // Create new user
    const newUser = {
      id: users.length + 1,
      email,
      firstName,
      lastName,
      accountType,
      subscription: {
        plan,
        limits: subscription,
        active: true,
        createdAt: new Date().toISOString(),
      },
      apiToken: `user_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`,
      createdAt: new Date().toISOString(),
    }

    users.push(newUser)

    // Return user data (excluding password)
    return NextResponse.json({
      user: {
        id: newUser.id,
        email: newUser.email,
        firstName: newUser.firstName,
        lastName: newUser.lastName,
        subscription: newUser.subscription,
      },
    })
  } catch (error) {
    console.error("Registration error:", error)
    return NextResponse.json({ error: "Failed to register user" }, { status: 500 })
  }
}
