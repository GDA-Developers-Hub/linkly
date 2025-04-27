import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

export function middleware(request: NextRequest) {
  // Return next response without any restrictions
  return NextResponse.next()
}

// Remove matcher config to avoid applying middleware to any routes
export const config = {
  matcher: [],
}
