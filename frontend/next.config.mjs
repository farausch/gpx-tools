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
    output: "standalone"
};

export default nextConfig;
