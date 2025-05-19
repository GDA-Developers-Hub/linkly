export class AuthAPI {
  private readonly backendBase =
    process.env.API_URL || "http://localhost:8000";

  // Redirect to link a social account
  link(provider: "google" | "facebook" | "linkedin" | "twitter") {
    let url;
    if (provider === "linkedin") {
      url = `${this.backendBase}/accounts/oidc/${provider}/login/?process=connect`;
    } else {
      url = `${this.backendBase}/accounts/${provider}/login/?process=connect`;
    }
    window.location.href = url;
  }
}
