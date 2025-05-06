/*
 * MIDDLEWARE REFERENCE (DISABLED)
 * 
 * This file contains the original middleware code for reference only.
 * No middleware functionality is exported from this file.
 * 
 * Next.js static export (`output: 'export'` in next.config.js) is incompatible with middleware.
 * 
 * To restore middleware functionality:
 * 1. Remove `output: 'export'` from next.config.js
 * 2. Rename this file back to middleware.ts
 */

// This code is not exported, just kept for reference
const originalMiddleware = `
import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

export function middleware(request: NextRequest) {
  const token = request.cookies.get("token")?.value
  const { pathname } = request.nextUrl

  // Protected routes (require authentication)
  if (pathname.startsWith("/dashboard")) {
    if (!token) {
      return NextResponse.redirect(new URL("/auth/login", request.url))
    }
  }

  // Auth routes (accessible only when not authenticated)
  if (pathname.startsWith("/auth/") && token) {
    return NextResponse.redirect(new URL("/dashboard", request.url))
  }

  return NextResponse.next()
}

// Configure middleware to run on specific paths
export const config = {
  matcher: [
    // Protected routes
    "/dashboard/:path*",
    // Auth routes
    "/auth/:path*",
  ],
}
`
