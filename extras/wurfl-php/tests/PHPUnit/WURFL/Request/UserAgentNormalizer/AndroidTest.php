<?php
/**
 * test case
 */
require_once 'BaseTest.php';

/**
 * test case.
 */
class WURFL_Request_UserAgentNormalizer_AndroidTest extends WURFL_Request_UserAgentNormalizer_BaseTest {


    function setUp() {
        $this->normalizer = new WURFL_Request_UserAgentNormalizer_Specific_Android();
    }

    /**
     * @test
     * @dataProvider normalizerDataProvider
     *
     */
    function trimsToTwoDigitTheOsVersion($userAgent, $expected) {
        $found = $this->normalizer->normalize($userAgent);
        $this->assertEquals($expected, $found);
    }

    function normalizerDataProvider() {
        return array(
            array("FOO", "FOO"),
            array("Mozilla/5.0 (Linux; U; Android 1.0.15; fr-fr; A70HB Build/CUPCAKE) AppleWebKit/525.10+ (KHTML, like Gecko) Version/3.0.4 Mobile Safari/523.12.2",
                "Mozilla/5.0 (Linux; U; Android 1.0; fr-fr; A70HB Build/CUPCAKE) AppleWebKit/525.10+ (KHTML, like Gecko) Version/3.0.4 Mobile Safari/523.12.2"),
            array("Mozilla/5.0 (Linux; U; Android 2.1-update1; en-us; Hero Build/ERE27) AppleWebKit/525.10+ (KHTML, like Gecko) Version/3.0.4 Mobile Safari/523.12.2",
                "Mozilla/5.0 (Linux; U; Android 2.1; en-us; Hero Build/ERE27) AppleWebKit/525.10+ (KHTML, like Gecko) Version/3.0.4 Mobile Safari/523.12.2"),
            array("Mozilla/5.0 (Linux; U; Android 2.2.1; en-us; myTouchHD Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
                "Mozilla/5.0 (Linux; U; Android 2.2; en-us; myTouchHD Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1")
        );

    }

}
