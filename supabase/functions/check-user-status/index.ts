import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

serve(async (req: Request) => {
  try {
    const { identifier } = await req.json();

    if (!identifier || typeof identifier !== "string") {
      throw new Error("Identifier is required.");
    }

    const supabaseUrl = Deno.env.get("SUPABASE_URL");
    const serviceRoleKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");

    if (!supabaseUrl || !serviceRoleKey) {
      throw new Error("Supabase service role credentials are not configured.");
    }

    const adminClient = createClient(supabaseUrl, serviceRoleKey, {
      auth: { autoRefreshToken: false, persistSession: false },
    });

    const normalized = identifier.trim().toLowerCase();
    let page = 1;
    let found = false;

    while (!found) {
      const { data, error } = await adminClient.auth.admin.listUsers({
        page,
        perPage: 200,
      });

      if (error) throw error;

      const users = data.users ?? [];
      if (users.length === 0) break;

      found = users.some((user) => {
        const email = user.email?.toLowerCase();
        const phone = user.phone?.toLowerCase();
        return email == normalized || phone == normalized;
      });

      if (users.length < 200) break;
      page += 1;
    }

    return new Response(
      JSON.stringify({
        exists: found,
        identifier: normalized,
      }),
      {
        headers: { "Content-Type": "application/json" },
        status: 200,
      },
    );
  } catch (err: unknown) {
    const errorMessage = err instanceof Error ? err.message : "Unknown error";
    return new Response(JSON.stringify({ error: errorMessage }), {
      headers: { "Content-Type": "application/json" },
      status: 400,
    });
  }
});
