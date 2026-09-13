import { Html, Head, Main, NextScript } from "next/document";

// Without this, mobile browsers render the site at a ~980px desktop
// viewport and shrink it — nothing looks responsive.
export default function Document() {
  return (
    <Html lang="en">
      <Head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
