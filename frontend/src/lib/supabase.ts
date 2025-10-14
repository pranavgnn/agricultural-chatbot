import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://wdakyaacjmbgovhagrye.supabase.co'
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndkYWt5YWFjam1iZ292aGFncnllIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA0NDA2ODksImV4cCI6MjA3NjAxNjY4OX0.8C-c2t-u_3y6QvasCSDGtzvgLxteCkrMmUe_vcLaWBE'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
