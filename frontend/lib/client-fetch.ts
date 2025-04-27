export async function fetchData<T>(url: string): Promise<T> {
  try {
    // In a real app, this would make an actual API call
    // For demo purposes, we'll simulate a delay and return mock data
    await new Promise((resolve) => setTimeout(resolve, 500))

    // This is a placeholder - in a real app, you would fetch from your API
    // return await fetch(url).then(res => res.json());

    // For now, we'll throw an error to trigger the fallback data in components
    throw new Error("API not implemented yet")
  } catch (error) {
    console.error(`Error fetching data from ${url}:`, error)
    throw error
  }
}
