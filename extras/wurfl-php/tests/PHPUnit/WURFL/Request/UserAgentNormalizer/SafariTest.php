<?php
/**
 * test case
 */

/**
 * test case.
 */
class WURFL_Request_UserAgentNormalizer_SafariTest extends WURFL_Request_UserAgentNormalizer_BaseTest {
	

	function setUp() {
		$this->normalizer = new WURFL_Request_UserAgentNormalizer_Specific_Safari ();
	}
	
	/**
	 * @test
	 * @dataProvider safariUserAgentsProvider
	 */
	function shoudReturnTheTypeWithTheSafariMajorVersion($userAgent, $expected) {
		$this->assertNormalizeEqualsExpected ( $userAgent, $expected );
	}
	
	function safariUserAgentsProvider() {
		return array(
			   array(
                        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_4_11; fr) AppleWebKit/525.18 (KHTML, like Gecko) Version/3.1.1 Safari/525.18"
                        , "Mozilla/5.0 (Macintosh; U; Safari/525"
                    ),
                array("Safari/525", "Safari/525"),
                array("Mozilla", "Mozilla"),
                array("Firefox", "Firefox")
		
		);
	}

}

