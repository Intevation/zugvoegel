module.exports = {
  root: true,

  env: {
    node: true
  },

  // https://eslint.vuejs.org/rules/
  extends: [
    "eslint:recommended",
    "plugin:vue/recommended"
  ],

  rules: {
    // https://eslint.org/docs/rules/no-console
    "no-console": process.env.NODE_ENV === "production" ? "error" : "off",
    // https://eslint.org/docs/rules/no-debugger
    "no-debugger": process.env.NODE_ENV === "production" ? "error" : "off",
    // https://eslint.org/docs/rules/key-spacing
    "key-spacing": [1, {"beforeColon": false, "afterColon": true}],
    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/html-closing-bracket-newline.md
    "vue/html-closing-bracket-newline": [
      "error",
      {
        singleline: "never",
        multiline: "never"
      }
    ],
    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/html-closing-bracket-spacing.md
    "vue/html-closing-bracket-spacing": [
      "error",
      {
        startTag: "never",
        endTag: "never",
        selfClosingTag: "always"
      }
    ]
  },
  parser: "vue-eslint-parser",
  parserOptions: {
    parser: "babel-eslint"
  }
};