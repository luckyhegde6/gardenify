import { Redirect } from "expo-router";
import { useAuth } from "@/hooks/use-auth";
import { Loading } from "@/components/loading";

export default function Index() {
  const { user, loading } = useAuth();

  if (loading) return <Loading message="Loading..." />;

  return <Redirect href={user ? "/(tabs)" : "/(auth)/login"} />;
}
