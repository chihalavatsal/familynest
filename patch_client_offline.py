with open("frontend/src/api/client.ts", "r") as f:
    content = f.read()

do_request_block = """
  const doRequest = async (authHeader?: string): Promise<Response> => {
    if (authHeader) headers['Authorization'] = authHeader;
    return fetch(`${BASE_URL}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
      signal,
    });
  };

  let res = await doRequest();"""

safe_do_request = """
  const doRequest = async (authHeader?: string): Promise<Response> => {
    if (authHeader) headers['Authorization'] = authHeader;
    try {
      return await fetch(`${BASE_URL}${path}`, {
        method,
        headers,
        body: body !== undefined ? JSON.stringify(body) : undefined,
        signal,
      });
    } catch (error) {
      if (!navigator.onLine || (error instanceof TypeError && error.message.includes('fetch'))) {
        throw { status: 0, message: "You're offline. We couldn't reach FamilyNest. Check your connection and try again." } as ApiError;
      }
      throw error;
    }
  };

  let res = await doRequest();"""

if "You're offline" not in content:
    content = content.replace(do_request_block, safe_do_request)
    
with open("frontend/src/api/client.ts", "w") as f:
    f.write(content)
