import re
with open("frontend/src/App.tsx", "r") as f:
    code = f.read()

import_query = "from '@tanstack/react-query';\n"
if "QueryClient" not in code:
    code = code.replace("import { AuthProvider } from './store/AuthContext';", "import { AuthProvider } from './store/AuthContext';\nimport { QueryClient, QueryClientProvider } from '@tanstack/react-query';")

    query_client_init = """
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      refetchOnWindowFocus: true,
      retry: 1,
    },
  },
});
"""
    code = code.replace("function App() {", query_client_init + "\nfunction App() {")

    code = code.replace("<AuthProvider>", "<QueryClientProvider client={queryClient}>\n      <AuthProvider>")
    code = code.replace("</AuthProvider>", "</AuthProvider>\n    </QueryClientProvider>")

with open("frontend/src/App.tsx", "w") as f:
    f.write(code)
