import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { Resend } from 'npm:resend';

// @ts-ignore: Deno is available in the Supabase Edge Function runtime
const resend = new Resend(Deno.env.get('RESEND_API_KEY'));

serve(async (req: Request) => {
  try {
    const { template, email, data } = await req.json();

    let html = '';
    let subject = '';

    // Template Mapping logic
    switch (template) {
      case 'subscription_active':
        subject = 'Welcome to Super LeoBook Elite';
        html = `
          <html>
            <body style="background-color: #000000; color: #ffffff; font-family: sans-serif; text-align: center; padding: 40px;">
              <h1 style="color: #d4af37;">LOBOOK</h1>
              <h2>Elite Status Confirmed.</h2>
              <p>Your Super LeoBook subscription was activated on ${data.activation_date}.</p>
              <p>Enjoy premium autonomous access.</p>
            </body>
          </html>
        `;
        break;

      case 'login_alert': {
        const forwardedFor = req.headers.get('x-forwarded-for') ??
          req.headers.get('cf-connecting-ip') ??
          req.headers.get('x-real-ip') ??
          'Unavailable';
        const device = data?.device ?? {};
        subject = 'New LeoBook sign-in detected';
        html = `
          <html>
            <body style="background-color: #000000; color: #ffffff; font-family: sans-serif; padding: 40px;">
              <h1 style="color: #d4af37;">LEOBOOK</h1>
              <h2>New sign-in detected</h2>
              <p>We noticed a successful sign-in on your LeoBook account.</p>
              <p><strong>Identifier:</strong> ${data?.identifier ?? email}</p>
              <p><strong>IP Address:</strong> ${forwardedFor}</p>
              <p><strong>Platform:</strong> ${device.platform ?? 'Unknown'}</p>
              <p><strong>Device:</strong> ${device.model ?? device.device ?? 'Unknown'}</p>
              <p><strong>Logged in at:</strong> ${data?.logged_in_at ?? 'Unknown'}</p>
            </body>
          </html>
        `;
        break;
      }
      
      case 'trial_reminder':
        subject = 'Your LeoBook Trial Ends in 15 Days';
        html = `
          <html>
            <body style="background-color: #000000; color: #ffffff; font-family: sans-serif; text-align: center; padding: 40px;">
              <h1>LOBOOK</h1>
              <h2 style="color: #ff3b30;">15 Days Left.</h2>
              <p>Your free trial is nearly over. Upgrade to Super LeoBook now to keep your elite features.</p>
            </body>
          </html>
        `;
        break;

      default:
        throw new Error('Invalid template');
    }

    const { data: res, error } = await resend.emails.send({
      from: 'onboarding@resend.dev',
      to: [email],
      subject: subject,
      html: html,
    });

    if (error) throw error;

    return new Response(JSON.stringify(res), { 
      headers: { 'Content-Type': 'application/json' },
      status: 200 
    });

  } catch (err: unknown) {
    const errorMessage = err instanceof Error ? err.message : 'Unknown error';
    return new Response(JSON.stringify({ error: errorMessage }), { 
      headers: { 'Content-Type': 'application/json' },
      status: 400 
    });
  }
})
