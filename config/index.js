const path = require('path');

module.exports = {
  projectName: 'brainactive',
  date: '2026-04-24',
  designWidth: 750,
  deviceRatio: {
    '375': 2 / 1,
    '640': 1 / 1,
    '750': 750 / 750,
    '828': 1 / 1,
  },
  sourceRoot: 'src',
  outputRoot: 'dist/h5',
  plugins: [],
  define: {
    'process.env.TARO_ENV': JSON.stringify(process.env.TARO_ENV || 'h5'),
  },
  alias: {
    '@': path.resolve(__dirname, '..', 'src'),
  },
  compiler: 'webpack5',
  cache: {
    enable: false,
  },
  targets: ['h5'],
  h5: {
    staticDirectory: 'static',
    publicPath: '/',
    miniCssExtractPluginOption: {
      ignoreOrder: true,
      filename: 'css/[name].css',
    },
  },
  framework: 'react',
};
