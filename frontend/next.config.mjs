/** @type {import('next').NextConfig} */
const nextConfig = {
    async rewrites() {
        return [
            {
                source: '/backend/:path*',
                destination: `${process.env.BACKEND_URL}/:path*`
            }
        ]
    },
};

export default nextConfig;
