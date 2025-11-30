-- 1. Check if users exist in auth.users
SELECT count(*) as user_count FROM auth.users;

-- 2. Insert profiles for existing users who don't have one
INSERT INTO public.profiles (id, email, full_name)
SELECT 
    id, 
    email, 
    raw_user_meta_data->>'full_name' as full_name
FROM auth.users
WHERE id NOT IN (SELECT id FROM public.profiles);

-- 3. Verify profiles again
SELECT * FROM public.profiles;
