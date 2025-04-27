import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Get token from cookies or localStorage (cookies preferred for SSR)
  const token = request.cookies.get("linkly_access_token")?.value || request.headers.get("Authorization")?.split(" ")[1]

  // Check if the path is protected
  const isProtectedRoute = pathname.startsWith("/dashboard")
  const isAuthRoute = pathname.startsWith("/auth")

  // If trying to access protected route without token, redirect to login
  if (isProtectedRoute && !token) {
    return NextResponse.redirect(new URL("/auth/login", request.url))
  }

  // If trying to access auth routes with token, redirect to dashboard
  if (isAuthRoute && token) {
    return NextResponse.redirect(new URL("/dashboard", request.url))
  }

  return NextResponse.next()
}

// Only run middleware on specific paths
export const config = {
  matcher: ["/dashboard/:path*", "/auth/:path*"],
}
