/** @type {import('next').NextConfig} */
const nextConfig = {
    output: "standalone",
    images: {
        remotePatterns: [
            {
                protocol: 'https',
                hostname: 'res.cloudinary.com',
            },
            {
                protocol: 'https',
                hostname: 'images.unsplash.com',
            },
        ],
    },
    webpack: (config, { dev }) => {
        if (dev) {
            config.module.rules.push({
                test: /\.(jsx|tsx)$/,
                exclude: /node_modules/,
                enforce: "pre",
                use: "@dyad-sh/nextjs-webpack-component-tagger",
            });
        }
        return config;
    },
};
export default nextConfig;
