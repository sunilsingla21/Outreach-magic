import path from 'path';
const pages = [
    'base',
    'user/hosts',
    'user/emails',
    'user/emailGroups',
    'user/seeds',
    'user/smartlead',
    'user/vps',
    'google/add',
    'yahoo/add',
];

export default {
    entry: pages.reduce((config, page) => {
        config[page] = `./src/js/${page}/index.js`;
        return config;
    }, {}),
    output: {
        filename: '[name].bundle.js',
        path: path.resolve('./app/static/dist/'),
    },
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                },
            },
        ],
    },
};
