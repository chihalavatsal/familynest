with open("frontend/src/components/layout/AppShell.tsx", "r") as f:
    content = f.read()

import_str = "import { WifiOff } from 'lucide-react';\n"
content = import_str + content

hook_str = """  const [isOffline, setIsOffline] = useState(!navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOffline(false);
    const handleOffline = () => setIsOffline(true);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);
"""

content = content.replace("  const location = useLocation();", "  const location = useLocation();\n" + hook_str)

offline_banner = """
      {isOffline && (
        <div className="bg-red-50 text-red-600 px-4 py-2 text-sm font-medium text-center flex items-center justify-center gap-2 z-50 relative">
          <WifiOff className="w-4 h-4" />
          You're offline. FamilyNest needs an internet connection to load your latest family data.
        </div>
      )}
"""

content = content.replace("    <div className=\"fn-app-layout\">", "    <div className=\"fn-app-layout\">\n" + offline_banner)

with open("frontend/src/components/layout/AppShell.tsx", "w") as f:
    f.write(content)
