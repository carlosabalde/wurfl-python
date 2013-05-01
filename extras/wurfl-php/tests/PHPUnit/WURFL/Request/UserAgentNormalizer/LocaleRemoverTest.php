<?php
/**
 * test case
 */

require_once 'BaseTest.php';

/**
 * test case.
 */
class WURFL_Request_UserAgentNormalizer_LocaleRemoverTest extends WURFL_Request_UserAgentNormalizer_BaseTest {


	function setUp() {
		$this->normalizer = new WURFL_Request_UserAgentNormalizer_Generic_LocaleRemover();
	}

	/**
	 * @test
	 * @dataProvider userAgentsDataProvider
	 *
	 */
	function shoudRemoveTheLocaleFromTheUserAgent($userAgent, $expected) {
		$found = $this->normalizer->normalize($userAgent);
		$this->assertEquals($found, $expected);
	}

	function userAgentsDataProvider() {
		return array (
			array ("Mozilla/5.0 (X11; U; Linux armv6l; en-US; rv:1.9a6pre) Gecko/20070810 Firefox/3.0a1", "Mozilla/5.0 (X11; U; Linux armv6l; rv:1.9a6pre) Gecko/20070810 Firefox/3.0a1" ),
			array ("Mozilla/5.0 (SymbianOS/9.1; U; en-us) AppleWebKit/414 (KHTML, like Gecko) Safari/414 es61", "Mozilla/5.0 (SymbianOS/9.1; U) AppleWebKit/414 (KHTML, like Gecko) Safari/414 es61" ),
			array ("Mozilla/5.0 (SymbianOS/9.1; U; en-us) AppleWebKit/413 (KHTML, like Gecko) Safari/413", "Mozilla/5.0 (SymbianOS/9.1; U) AppleWebKit/413 (KHTML, like Gecko) Safari/413"),
            array ("Android (Linux; U; Android 1.5; zh-cn; hero) AppleWebKit/528.5+ (KHTML) Version/3.1.2", "Android (Linux; U; Android 1.5; hero) AppleWebKit/528.5+ (KHTML) Version/3.1.2" ),
            array ("HTC_Dream Mozilla/5.0 (Linux; U; Android 1.5; it-; Build/CRB43) AppleWebKit/528.5+ (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1", "HTC_Dream Mozilla/5.0 (Linux; U; Android 1.5; Build/CRB43) AppleWebKit/528.5+ (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1" ),
            array ("Mozilla/5.0 (Linux; U; Android 0.5; en-us) AppleWebKit/522+ (KHTML, like Gecko) Safari/419.3", "Mozilla/5.0 (Linux; U; Android 0.5) AppleWebKit/522+ (KHTML, like Gecko) Safari/419.3" ),
            array ("Mozilla/5.0 (Linux; U; Android 0.6; en-us; generic) AppleWebKit/525.10+ (KHTML, like Gecko) Version/3.0.4 Mobile Safari/523.12.2", "Mozilla/5.0 (Linux; U; Android 0.6; generic) AppleWebKit/525.10+ (KHTML, like Gecko) Version/3.0.4 Mobile Safari/523.12.2" ),
            array ("Mozilla/5.0 (Linux; U; Android 1.0; en-us; dream) AppleWebKit/525.10+ (KHTML, like Gecko) Version/3.0.4 Mobile Safari/523.12.2", "Mozilla/5.0 (Linux; U; Android 1.0; dream) AppleWebKit/525.10+ (KHTML, like Gecko) Version/3.0.4 Mobile Safari/523.12.2" ),
            array ("Mozilla/5.0 (Linux; U; Android 1.1; en-us; generic) AppleWebKit/525.10+ (KHTML, like Gecko) Version/3.0.4 Mobile Safari/523.12.2", "Mozilla/5.0 (Linux; U; Android 1.1; generic) AppleWebKit/525.10+ (KHTML, like Gecko) Version/3.0.4 Mobile Safari/523.12.2" ),
            array ("Mozilla/5.0 (Linux; U; Android Blur_Version.0.6.13.morrison.Blurdev.en.US; en-us; generic) AppleWebKit/528.5+ (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1", "Mozilla/5.0 (Linux; U; Android Blur_Version.0.6.13.morrison.Blurdev.en.US; generic) AppleWebKit/528.5+ (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1" ),
            array ("Mozilla/5.0 (Linux; U; Android 1.5; de-de; HTC Magic Build/CRA86) AppleWebKit/528.5+ (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1", "Mozilla/5.0 (Linux; U; Android 1.5; HTC Magic Build/CRA86) AppleWebKit/528.5+ (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1" ),
            array ("Mozilla/5.0 (Linux; U; Android 1.5; en-gb; HTC Magic Build/CRA71C) AppleWebKit/528.5+ (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1", "Mozilla/5.0 (Linux; U; Android 1.5; HTC Magic Build/CRA71C) AppleWebKit/528.5+ (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1" ),
            array ("Mozilla/5.0 (Linux; U; Android 2.1-update1; de-de; HTC Hero Build/ERE27) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17", "Mozilla/5.0 (Linux; U; Android 2.1-update1; HTC Hero Build/ERE27) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17" ),
            array ("Mozilla/5.0 (X11; U; Linux armv7l; en-GB; rv:1.9.2a1pre) Gecko/20090928 Firefox/3.5 Maemo Browser 1.4.1.21 RX-51 N900", "Mozilla/5.0 (X11; U; Linux armv7l; rv:1.9.2a1pre) Gecko/20090928 Firefox/3.5 Maemo Browser 1.4.1.21 RX-51 N900"),
            array ("Mozilla", "Mozilla" ),
			array ("Firefox", "Firefox" )
		);

	}

}

