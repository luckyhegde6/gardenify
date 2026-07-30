import { useState, useEffect, useCallback } from "react";
import { Platform } from "react-native";
import * as Notifications from "expo-notifications";
import * as Device from "expo-device";
import { supabase } from "@/lib/supabase";
import { useAuth } from "@/hooks/use-auth";

export function useNotifications() {
  const { user } = useAuth();
  const [expoPushToken, setExpoPushToken] = useState<string | null>(null);
  const [notificationPermission, setNotificationPermission] =
    useState<boolean>(false);

  const registerForPushNotifications = useCallback(async () => {
    if (!Device.isDevice) {
      return null;
    }

    const { status: existingStatus } =
      await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;

    if (existingStatus !== "granted") {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }

    if (finalStatus !== "granted") {
      setNotificationPermission(false);
      return null;
    }

    setNotificationPermission(true);

    try {
      const tokenData = await Notifications.getExpoPushTokenAsync();
      const token = tokenData.data;
      setExpoPushToken(token);

      if (user) {
        await supabase
          .from("user_settings")
          .upsert(
            { user_id: user.id, push_token: token },
            { onConflict: "user_id" },
          );
      }

      return token;
    } catch {
      return null;
    }
  }, [user]);

  useEffect(() => {
    registerForPushNotifications();
  }, [registerForPushNotifications]);

  useEffect(() => {
    if (Platform.OS === "android") {
      Notifications.setNotificationChannelAsync("default", {
        name: "default",
        importance: Notifications.AndroidImportance.MAX,
        vibrationPattern: [0, 250, 250, 250],
        lightColor: "#208AEF",
      });
    }
  }, []);

  return {
    expoPushToken,
    notificationPermission,
    registerForPushNotifications,
  };
}
