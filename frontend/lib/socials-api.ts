export class AuthAPI {
  private readonly backendBase =
    process.env.API_URL || "http://localhost:8000";

  // Redirect to link a social account
  link(provider: "google" | "facebook" | "linkedin" | "twitter") {
    const token = localStorage.getItem("linkly_access_token")
    let url;
    if (provider === "linkedin") {
      url = `${this.backendBase}/accounts/oidc/${provider}/login/?process=connect&token=${token}`;
    } else {
      url = `${this.backendBase}/accounts/${provider}/login/?process=connect&token=${token}`;
    }
    window.location.href = url;
  }
}
