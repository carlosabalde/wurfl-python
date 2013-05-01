<?php
/**
 * test case
 */

require_once 'BaseTest.php';

/**
 * test case.
 */
class WURFL_Request_UserAgentNormalizer_LGUPLUSTest extends WURFL_Request_UserAgentNormalizer_BaseTest {


	function setUp() {
		$this->normalizer = new WURFL_Request_UserAgentNormalizer_Specific_LGUPLUSNormalizer();
	}

	/**
	 * @test
	 * @dataProvider lguplusUserAgentsDataProvider
	 *
	 */
	function shouLd($userAgent, $expected) {
		$found = $this->normalizer->normalize($userAgent);
		$this->assertEquals($found, $expected);
	}

	function lguplusUserAgentsDataProvider() {
		return array (
			array ("Mozilla/4.0 (compatible;MSIE 7.0;Windows NT 5.2;480*800;WV02.00.01;;lgtelecom;EB10-20100621-717721593;LG-LU9400;0)",
                    "LG-LU9400 Windows NT WV"),
            array ("Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0;480*800;POLARIS 6.201;em1.0;WIFI;lgtelecom; EB10-20100804-178697799;LG-LU9400;0)",
                    "LG-LU9400 Windows NT POLARIS"),

            array ("Mozilla/4.0 (compatible; MSIE 6.0; Windows CE;480*800;POLARIS 6.100;em1.0;lgtelecom;EB10-20101006-720032348;SHW-M7350;0)",
                    "SHW-M7350 Windows CE POLARIS"),

            array ("Mozilla/4.0(compatible;MSIE 7.0;Windows NT 5.2;480*800;WV02.00.01;;lgtelecom;EB10-20100819-719028161;SHW-M130L;0)",
                    "SHW-M130L Windows NT WV"),
            array ("Mozilla/5.0 (Linux; U; Android 2.2; ko-kr; LG-LU3000 Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1;LGUPLUS;01.00.00;WIFI; EB10-20100804-178697799;0",
                    "Mozilla/5.0 (Linux; U; Android 2.2; ko-kr; LG-LU3000 Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1;LGUPLUS;01.00.00;WIFI; EB10-20100804-178697799;0"),
                                    
			array ("Firefox/3.x", "Firefox/3.x" ),
			array ("Mozilla", "Mozilla" ),
			array ("Firefox", "Firefox" )
		);

	}

}

